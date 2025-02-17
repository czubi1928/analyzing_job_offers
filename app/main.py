import os

from database import Database
from extraction import Extraction
from logger import Logger
from utilities import Utilities


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Class to logging messages
    logger = Logger()

    # Class to support some utilities
    ut = Utilities(logger)

    # Class to connect with database and database actions
    db = Database(logger)

    # Path to file .txt with job offers
    offers_file = os.path.join(project_root, 'data', 'it_offers.txt')

    # A tool for finding links with a “baked” *.txt file and rewriting to a nice form.
    # Uncomment if you want to rewrite the file with offers
    """
    raw_offers_file = os.path.join(project_root, 'data', 'raw', 'it_offers_raw.txt')
    ut.sort_raw_offers_file(raw_offers=raw_offers_file, output_offers=offers_file, backup=True)
    """

    sites_structure = os.path.join(project_root, 'app', 'sites_structure.json')

    offers_sites = ut.load_supported_sites(sites_structure)

    if not offers_sites:
        logger.warning("There are no offers in the file!")
        exit()

    # Uploading links to job listings
    with open(offers_file, "r", encoding="utf-8") as file:
        offers = [line.strip() for line in file if line.strip()]

    # We initialize the Extraction class
    downloaded_offers = os.path.join(project_root, 'data', 'raw', 'downloaded_sites')

    ex = Extraction(logger, db, offers_sites, downloaded_offers)

    # extraction for files
    try:
        for path in os.listdir(downloaded_offers):
            # site = ut.is_valid_url(offer, offers_sites)
            site = "justjoin.it"  # na sztywno narazie

            if site is not None:
                full_path = os.path.join(downloaded_offers, path)
                ex.file_extraction(full_path, site)
    except FileNotFoundError as e:
        logger.warning(f"There is no file with downloaded sites: {e}")
    """
    # extraction for sites
    for offer in offers:
        site = ut.is_valid_url(offer, offers_sites)

        if site is not None:
            ex.link_extraction(offer, site)
    """
    db.close_connection()


if __name__ == '__main__':
    main()
