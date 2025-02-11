import json
import os

from app.database import Database
from app.logger import Logger


def extract(file, logger):
    """
    Loads JSON data from the specified JSON file.

    :param logger:  The logger object.
    :param file:    The path to the JSON file.
    :return:        List of loaded data from the file.
    """
    all_data = []

    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.extend(data)
    except Exception as e:
        logger.error(f"An error occurred while loading data from {file}: {e}")

    return all_data


def transform(data, logger):
    """
    Processes JSON data into a format suitable for the database.

    :param logger:  The logger object.
    :param data:    List of jobs loaded from JSON.
    :return:        List of dictionaries ready for insertion into the database.
    """
    transformed_data = []

    try:
        for offer in data:
            base_data = {
                'title': offer['title'],
                'company': offer['company_name'],
                'location': offer.get('city', '').lower(),
                'category': offer.get('marker_icon', '').lower(),
                'date_add': offer.get('published_at', '').lower().replace('t', ' ').replace('z', ''),
                'salary': json.dumps(
                    {
                        emp.get('type', ''): {
                            'from': emp.get('salary', {}).get('from') if emp.get('salary') else None,
                            'to': emp.get('salary', {}).get('to') if emp.get('salary') else None,
                            'currency': emp.get('salary', {}).get('currency') if emp.get('salary') else None
                        } for emp in offer.get('employment_types', []) or []
                    }
                ),
                'experience': offer.get('experience_level', '').lower(),
                'employment': ', '.join(emp.get('type', '') for emp in offer.get('employment_types', []) or []).lower(),
                'operating_mode': offer.get('workplace_type', '').lower(),
                'tech_stack': json.dumps({skill['name']: skill['level'] for skill in offer.get('skills', []) or []}),
                'link': 'https://justjoin.it/job-offer/' + offer.get('id', ''),  # offer.get('company_url', ''),
                'source': 'justjoin.it'  # Możesz ustawić stałą nazwę źródła
            }

            transformed_data.append(base_data)

        return transformed_data
    except Exception as e:
        logger.error(f"An error occurred while transforming data: {e}")
        return []


def etl() -> None:
    processed_files = 0

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    logger = Logger(log_folder=os.path.join(project_root, 'logs'))
    db = Database(logger, db_folder=os.path.join(project_root, 'data'))

    path_to_offers = os.path.join(project_root, 'data', 'raw', 'downloaded_offers',
                                  'justjoinit-job-offers-data-2021-10-2023-09')

    logger.info("The ETL process has begun...")

    """
    Searches a folder recursively for JSON files.

    :param path_to_offers:  The path from which we start the search.
    """
    for root, dirs, files in os.walk(path_to_offers):
        for file in files:
            if file.endswith(".json"):
                logger.debug(f"Found file {file} in {root}")

                extracted_data = extract(os.path.join(root, file), logger)
                transformed_data = transform(extracted_data, logger)

                if not transformed_data:
                    logger.warning(f"No data to insert from {file}")
                    continue
                else:
                    processed_files += 1
                    db.insert_job_offers_batch(transformed_data)

    logger.info(f"The ETL process has been completed successfully! Proccesed {processed_files} files.")

    db.close_connection()


if __name__ == "__main__":
    etl()
