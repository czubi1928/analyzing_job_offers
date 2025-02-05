import os
import sqlite3

import pandas as pd


class Database:
    def __init__(self, logger, db_name="job_offers.db", db_folder="data",
                 structure_location=os.path.join("data", "database_structure.sql")):
        self.logger = logger

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.connection = sqlite3.connect(os.path.join(project_root, db_folder, db_name))
        self.cursor = self.connection.cursor()
        self.create_structure(os.path.join(project_root, structure_location))

        # Get information about the columns in the job_offers table
        self.fields = [
            row[1] for row in self.cursor.execute("PRAGMA table_info(job_offers)")
            if row[1] not in ('id', 'position')  # pomijamy 'id' i 'position', jeśli nie wstawiamy do nich danych
        ]

    def create_structure(self, structure):
        with open(structure, 'r') as sql_file:
            sql_script = sql_file.read()

        try:
            self.cursor.executescript(sql_script)
            self.connection.commit()
            self.logger.info(f"Database structure from file {structure} was created successfully!")
        except (sqlite3.Error, AttributeError):
            self.logger.info(f"The database from file {structure} already exists!")
        except (sqlite3.Error, FileNotFoundError) as e:
            self.logger.error(f"Error while creating database structure: {e}.")

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            self.logger.info(f"Query executed successfully: {query}")

            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Error while executing query: {e}")

            return None

    def fetch_all_offers(self):
        query = "SELECT * FROM job_offers;"
        df = pd.read_sql_query(query, self.connection)

        return df

    def insert_job_offer(self, offer_data):
        # We build a SQL query and placeholders based on a list of fields
        columns = ', '.join(self.fields)
        placeholders = ', '.join(['?' for _ in self.fields])

        insert_data_query = f"""
    		INSERT INTO job_offers (
    			{columns}
    		) VALUES({placeholders});
    	"""

        # We generate a tuple of values based on the keys from offer_data
        # Assume that offer_data contains values for all keys in self.fields
        values = tuple(offer_data[field] for field in self.fields)

        # self.logger.debug(f"TEST - {values} // {offer_data['location']}")

        try:
            self.cursor.execute(insert_data_query, values)
            self.connection.commit()
            self.logger.info(
                f"The offer \"{offer_data['company']}, {offer_data['title']}, {offer_data['location'].capitalize()}\""
                f"has been added to the database!")
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"Duplicate entry or integrity error: {e}")
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")

    def insert_job_offers_batch(self, offers_data):
        # We are building a SQL query with placeholders
        columns = ', '.join(self.fields)
        placeholders = ', '.join(['?' for _ in self.fields])

        insert_data_query = f"""
            INSERT OR IGNORE INTO job_offers (
                {columns}
            ) VALUES ({placeholders});
        """

        # We create a list of values based on the input data
        values = [
            tuple(offer[field] for field in self.fields)
            for offer in offers_data
        ]

        try:
            # We are performing a batch insert
            self.cursor.executemany(insert_data_query, values)
            self.connection.commit()
            self.logger.info(f"{len(offers_data)} job offers have been added to the database!")
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"Integrity error during batch insert: {e}")
        except sqlite3.Error as e:
            self.logger.error(f"Database error during batch insert: {e}")

    def remove_older_duplicates(self):
        """
        Removes older duplicates from the job_offers table based on columns
        (title, company, category, location, source, link, operating_mode),
        leaving only the record with the highest (most recent) date_add value.

        Action:
        1) The subquery groups the listings by the above columns and selects MAX(date_add) as max_date.
        2) We remove all records whose rowid does not belong to the 'freshest' set in each group.
        """
        query = """
        DELETE FROM job_offers
        WHERE rowid NOT IN (
            SELECT a.rowid
            FROM job_offers a
            JOIN (
                SELECT 
                    title,
                    company,
                    category,
                    location,
                    source,
                    link,
                    operating_mode,
                    MAX(date_add) AS max_date
                FROM job_offers
                GROUP BY title, company, category, location, source, link, operating_mode
            ) b
              ON a.title = b.title
             AND a.company = b.company
             AND a.category = b.category
             AND a.location = b.location
             AND a.source = b.source
             AND a.link = b.link
             AND a.operating_mode = b.operating_mode
             AND a.date_add = b.max_date
        );
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            self.logger.info("Older duplicates have been removed successfully.")
        except Exception as e:
            self.logger.error(f"Error while removing duplicates: {e}")

    def create_temp_table(self):
        """
        Deletes the temporary table, if it exists, and then creates an empty table
        with the same structure as 'job_offers'.
        """
        try:
            self.cursor.execute("DROP TABLE IF EXISTS job_offers_temp;")

            # We will create an empty temporary table based on job_offers (without data)
            # Method 1: CREATE TABLE ... AS SELECT (without moving the records)
            create_temp = """
                CREATE TABLE job_offers_temp AS
                SELECT *
                FROM job_offers
                WHERE 1=0;
            """
            self.cursor.execute(create_temp)
            # self.cursor.execute("CREATE INDEX idx_offers_category ON job_offers (category);")
            # self.cursor.execute("CREATE INDEX idx_offers_date_add ON job_offers (date_add);")
            # self.cursor.execute("CREATE INDEX idx_offers_experience ON job_offers (experience);")
            # self.cursor.execute("CREATE INDEX idx_offers_location ON job_offers (location);")
            self.connection.commit()
            self.logger.debug("Temporary table 'job_offers_temp' was created successfully!")
        except sqlite3.Error as e:
            self.logger.error(f"Error while creating temp table: {e}")

    def fill_temp_table_with_filters(
            self,
            date_from=None,
            date_to=None,
            categories=None,
            locations=None,
            positions=None,
            experiences=None,
            operating_modes=None
    ):
        """
        Clears the temporary table (or creates it right away)
        and inserts records from 'job_offers' into it,
        taking into account the passed filters in the WHERE clause.
        """
        # Optionally, you can call create_temp_table() again each time:
        self.create_temp_table()
        # Now we are dynamically building a WHERE clause.
        conditions = []
        params = []

        if date_from:
            conditions.append("DATE(date_add) >= DATE(?)")
            params.append(date_from)

        if date_to:
            conditions.append("DATE(date_add) <= DATE(?)")
            params.append(date_to)

        if categories and len(categories) > 0:
            placeholders = ",".join(["?"] * len(categories))
            conditions.append(f"category IN ({placeholders})")
            params.extend(categories)

        if locations and len(locations) > 0:
            placeholders = ",".join(["?"] * len(locations))
            conditions.append(f"location IN ({placeholders})")
            params.extend(locations)

        if positions and len(positions) > 0:
            placeholders = ",".join(["?"] * len(positions))
            conditions.append(f"location IN ({placeholders})")
            params.extend(positions)

        if experiences and len(experiences) > 0:
            placeholders = ",".join(["?"] * len(experiences))
            conditions.append(f"experience IN ({placeholders})")
            params.extend(experiences)

        if operating_modes and len(operating_modes) > 0:
            placeholders = ",".join(["?"] * len(operating_modes))
            conditions.append(f"operating_mode IN ({placeholders})")
            params.extend(operating_modes)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        insert_query = f"""
            INSERT INTO job_offers_temp
            SELECT *
            FROM job_offers
            {where_clause};
        """
        self.logger.debug(f"Query: {insert_query}")

        try:
            self.cursor.execute(insert_query, params)
            self.connection.commit()
            self.logger.debug("Temp table was filled with filtered data.")
        except sqlite3.Error as e:
            self.logger.error(f"Error while filling temp table: {e}")

    def get_unique_categories(self):
        query = """
            SELECT DISTINCT category
            FROM job_offers
            WHERE category IS NOT NULL
            ORDER BY category;
        """
        df = pd.read_sql_query(query, self.connection)
        # We return a list of categories
        return df['category'].tolist()

    def get_unique_locations(self):
        query = """
            SELECT DISTINCT location
            FROM job_offers
            WHERE location IS NOT NULL
            ORDER BY location;
        """
        df = pd.read_sql_query(query, self.connection)
        return df['location'].tolist()

    def get_unique_positions(self):
        query = """
            SELECT DISTINCT position
            FROM job_offers
            WHERE position IS NOT NULL
            ORDER BY position;
        """
        df = pd.read_sql_query(query, self.connection)
        return df['position'].tolist()

    def get_unique_experiences(self):
        query = """
            SELECT DISTINCT experience
            FROM job_offers
            WHERE experience IS NOT NULL
            ORDER BY experience;
        """
        df = pd.read_sql_query(query, self.connection)
        return df['experience'].tolist()

    def get_unique_operating_modes(self):
        query = """
            SELECT DISTINCT operating_mode
            FROM job_offers
            WHERE operating_mode IS NOT NULL
            ORDER BY operating_mode;
        """
        df = pd.read_sql_query(query, self.connection)
        return df['operating_mode'].tolist()

    def get_offers_by_location(self):
        query = """
        SELECT location, COUNT(*) AS total_offers
        FROM job_offers_temp
        GROUP BY location
        ORDER BY total_offers DESC;
        """
        df = pd.read_sql_query(query, self.connection)

        return df

    def get_offers_by_experience(self):
        query = """
        SELECT experience, COUNT(*) AS total_offers
        FROM job_offers_temp
        GROUP BY experience
        ORDER BY total_offers DESC;
        """
        df = pd.read_sql_query(query, self.connection)

        return df

    def get_avg_salary_by_experience_and_currency(self):
        query = """
        WITH combined AS (
          SELECT 
            experience,
            UPPER(JSON_EXTRACT(salary, '$.b2b.currency')) AS currency,
            ROUND((JSON_EXTRACT(salary, '$.b2b.from') + JSON_EXTRACT(salary, '$.b2b.to')) / 2) AS b2b_value,
            NULL AS permanent_value
          FROM job_offers_temp
          WHERE salary IS NOT NULL
            AND JSON_EXTRACT(salary, '$.b2b.from') IS NOT NULL
            AND JSON_EXTRACT(salary, '$.b2b.to') IS NOT NULL
            AND JSON_EXTRACT(salary, '$.b2b.currency') IS NOT NULL
          UNION ALL
          SELECT 
            experience,
            UPPER(JSON_EXTRACT(salary, '$.permanent.currency')) AS currency,
            NULL AS b2b_value,
            ROUND((JSON_EXTRACT(salary, '$.permanent.from') + JSON_EXTRACT(salary, '$.permanent.to')) / 2) AS permanent_value
          FROM job_offers_temp
          WHERE salary IS NOT NULL
            AND JSON_EXTRACT(salary, '$.permanent.from') IS NOT NULL
            AND JSON_EXTRACT(salary, '$.permanent.to') IS NOT NULL
            AND JSON_EXTRACT(salary, '$.permanent.currency') IS NOT NULL
        )
        SELECT 
          experience,
          currency,
          ROUND(AVG(b2b_value)) AS avg_b2b_salary,
          ROUND(AVG(permanent_value)) AS avg_permanent_salary
        FROM combined
        GROUP BY experience, currency;
        """
        df = pd.read_sql_query(query, self.connection)

        return df

    def get_offers_by_year_month(self):
        query = """
        SELECT STRFTIME('%Y-%m', date_add) AS year_month,
               COUNT(*) AS total_offers
        FROM job_offers_temp
        GROUP BY STRFTIME('%Y-%m', date_add)
        ORDER BY year_month;
        """
        df = pd.read_sql_query(query, self.connection)

        return df

    def get_offers_by_operating_mode(self):
        query = """
        SELECT operating_mode, COUNT(*) AS total_offers
        FROM job_offers_temp
        GROUP BY operating_mode
        ORDER BY total_offers DESC;
        """
        df = pd.read_sql_query(query, self.connection)

        return df

    def get_technology_with_levels_sorted(self):
        """
        Returns a DataFrame with columns:
          - technology
          - skill_level
          - total_offers (for a pair (technology, skill_level))
          - total_for_tech (for all technology, regardless of level)
        Sorted so that the most popular technologies (globally) are the highest,
        and within technologies, levels are also sorted in descending order.
        """
        query = """
        WITH skill_count AS (SELECT json_each.key AS technology,
                                    CAST(json_each.value AS INT) AS skill_level,
                                    COUNT(*) AS total_offers
                             FROM job_offers_temp
                                      CROSS JOIN JSON_EACH(job_offers_temp.tech_stack)
                             GROUP BY json_each.key, json_each.value
            ),
             tech_count AS (SELECT json_each.key AS technology,
                                   COUNT(*) AS total_offers
                            FROM job_offers_temp
                                     CROSS JOIN JSON_EACH(job_offers_temp.tech_stack)
                            GROUP BY json_each.key
            )
        SELECT s.technology,
               s.skill_level,
               s.total_offers,
               t.total_offers AS total_for_tech
        FROM skill_count s
                 JOIN tech_count t ON s.technology = t.technology
        ORDER BY t.total_offers DESC, s.total_offers DESC;
        """
        df = pd.read_sql_query(query, self.connection)

        return df

    def close_connection(self):
        self.connection.close()
