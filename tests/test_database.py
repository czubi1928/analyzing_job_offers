import os

import pytest

from app.database import Database
from app.logger import Logger

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sample_offer = {
    "title": "Python Developer",
    "company": "Software House",
    "location": "warsaw",
    "link": "http://justjoin.it/python-offer",
    "date_add": "2023-01-01 10:00:00",
    "category": "python",
    "experience": "mid",
    "employment": "b2b",
    "operating_mode": "remote",
    "salary": '{"b2b": {"from": 10000, "to": 15000, "currency": "pln"}}',
    "tech_stack": '{"Python": 3, "Django": 3}',
    "source": "justjoin.it"
}


@pytest.fixture
def test_logger():
    """
    Creates a temporary .db file in the temporary directory.
    You can also return ':memory:' if you prefer an in-memory database.
    """
    return Logger(log_folder="tmp")


@pytest.fixture
def test_database(test_logger):
    """
    Fixture to create a Database object with temporary file and database structure.
    """
    db = Database(test_logger, db_folder="tmp")

    yield db  # wait for the test to run

    db.execute_query("DELETE FROM job_offers;")  # clear the table after the test
    db.close_connection()  # close connection after the test


def test_database_status(test_database):
    """
    Check that everything is fine with the database.
    """
    assert os.path.isfile(os.path.join(project_root, "tmp", "job_offers.db")), "Database does not exist..."

    # Retrieving information about components in the database
    info = test_database.fields

    # Make sure that the table exists
    assert test_database.fields, "Table 'job_offers' does not exist..."

    # Make sure that the table has the right columns
    for col in ["title", "company", "location"]:
        assert col in info, f"Column {col} is missing in the 'job_offers' table..."


def test_insert_offer(test_database):
    """
    Check inserting one prepared offer.
    """
    test_database.insert_job_offer(sample_offer)
    df = test_database.fetch_all_offers()
    assert len(df) == 1

    row = df.iloc[0]
    assert row["title"] == "Python Developer"
    assert row["company"] == "Software House"
    assert row["location"] == "warsaw"


def test_insert_duplicate_offer(test_database, caplog):
    """
    Check if the unique index works and the Logger warns when trying to insert a duplicate.
    """
    # Insert the second time (same title, company, location)
    test_database.insert_job_offer(sample_offer)
    test_database.insert_job_offer(sample_offer)

    df = test_database.fetch_all_offers()
    assert len(df) == 1, "Duplicate should not be inserted..."

    # Metoda insert_job_offer w razie konfliktu powinna logować ostrzeżenie lub informację
    # W kodzie Database.py np. self.logger.warning(...) lub self.logger.info(...) zależnie od implementacji.
    assert "Duplicate entry or integrity error" in caplog.text or "Database error" in caplog.text


'''
def test_remove_older_duplicates(test_database):
    """
    Przykładowy test dla metody remove_older_duplicates,
    jeśli w bazie masz zduplikowane wiersze i zostawiasz najnowszy.
    """
    # Dodajemy kilka duplikatów, różniących się date_add
    sample_offer = {
        "title": "Programista C++",
        "company": "Software Interactive Sp. z o.o.",
        "location": "warszawa",
        "link": "https://justjoin.it/job-offer/unique-link",
        "date_add": "2023-03-01 12:00:00",
        "category": "c++",
        "experience": "mid",
        "employment": "b2b",
        "operating_mode": "remote",
        "salary": '{"b2b": {"from": 13000, "to": 16000, "currency": "pln"}}',
        "tech_stack": '{"C++": 5}',
        "source": "justjoin.it"
    }
    # Wstawiamy kilka wersji z różnymi date_add
    sample_offer2 = dict(sample_offer, date_add="2023-03-05 09:00:00")
    sample_offer3 = dict(sample_offer, date_add="2023-02-25 10:00:00")

    test_database.insert_job_offer(sample_offer)
    test_database.insert_job_offer(sample_offer2)
    test_database.insert_job_offer(sample_offer3)

    df_before = test_database.fetch_all_offers()
    assert len(df_before) == 3, "Powinny być 3 wiersze (duplikaty)."

    # Usuwamy starsze duplikaty
    # (metoda remove_older_duplicates to Twój pomysł,
    #  który wybiera MAX(date_add) w każdej grupie i usuwa resztę)
    test_database.remove_older_duplicates()

    df_after = test_database.fetch_all_offers()
    assert len(df_after) == 1, "Powinien zostać tylko 1 najnowszy wpis."

    row = df_after.iloc[0]
    assert row["date_add"] == "2023-03-05 09:00:00", "Najświeższa data to 2023-03-05."
'''
