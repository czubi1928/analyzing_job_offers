from utilities import Utilities
from app.database import Database
from app.logger import Logger

from datetime import datetime
import json
import os


def find_json_files(path):
    """
    Przeszukuje rekurencyjnie folder w poszukiwaniu plików JSON.

    :param path: Ścieżka, od której rozpoczynamy wyszukiwanie.
    :return: Lista pełnych ścieżek do plików JSON.
    """

    threshold_date = datetime.strptime("2022-09", "%Y-%m")
    json_files = []

    for root, dirs, files in os.walk(path):
        folder_name = os.path.basename(root)

        try:
            folder_date = datetime.strptime(folder_name, "%Y-%m")

            if folder_date >= threshold_date:
                print(f"Przetwarzanie plików w folderze: {root}")

                for file in files:
                    if file.endswith(".json"):
                        json_files.append(os.path.join(root, file))
        except ValueError:
            # Jeśli nazwa folderu nie jest w formacie daty, pomiń
            print(f"Pominięto folder: {root} (nieprawidłowa nazwa)")

    return json_files


def extract(file):  # files
    """
    Wczytuje dane JSON z podanej listy plików.

    :param json_files: Lista ścieżek do plików JSON.
    :return: Lista załadowanych danych z plików.
    """

    all_data = []

    # for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_data.extend(data)  # Dodajemy dane z każdego pliku

    return all_data


def transform(data):
    """
    Przetwarza dane JSON do formatu odpowiedniego dla bazy danych.

    :param data: Lista ofert pracy wczytanych z JSON.
    :return: Lista słowników gotowych do wstawienia do bazy.
    """
    transformed_data = []
    for offer in data:
        # Przygotowanie wspólnych danych
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
            # 'type': ', '.join([emp.get('type', '') for emp in offer.get('employment_types', []) or []]),
            'experience': offer.get('experience_level', '').lower(),
            'employment': ', '.join(emp.get('type', '') for emp in offer.get('employment_types', []) or []).lower(),
            'operating_mode': offer.get('workplace_type', '').lower(),
            'tech_stack': json.dumps({skill['name']: skill['level'] for skill in offer.get('skills', []) or []}),
            'link': 'https://justjoin.it/job-offer/' + offer.get('id', ''),  # offer.get('company_url', ''),
            'source': 'justjoin.it'  # Możesz ustawić stałą nazwę źródła
        }
        transformed_data.append(base_data)

    return transformed_data


def process(path):
    """
    Przeprowadza proces ETL.

    :param path: Ścieżka początkowa do plików JSON.
    """
    json_files = find_json_files(path)

    for json_file in json_files:
        data = extract(json_file)
        transformed_data = transform(data)
        #for offer_data in transformed_data:
        #    db.insert_job_offer(offer_data)
        db.insert_job_offers_batch(transformed_data)


logger = Logger()

folder = "various_files"
ut = Utilities(logger, folder)

db_name = ut.add_folder("job_offers.db")
db_structure = ut.add_folder("database_structure.sql")
db = Database(logger, db_name, db_structure)

path = "C:\\Users\\pczub\\PycharmProjects\\analyzing_job_offers\\downloaded_offers"

process(path)
