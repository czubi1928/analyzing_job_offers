import json
import os
import re
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Utilities:
    def __init__(self, logger):
        self.logger = logger

    def sort_raw_offers_file(self, raw_offers, output_offers=os.path.join(project_root, 'data', 'it_offers.txt'),
                             backup=True):
        # Check if the input file exists
        if os.path.exists(raw_offers):
            # Initialize the links list
            links = []

            # Regular expression to match valid URLs
            url_pattern = re.compile(r"https?://[^\s]+")

            # Read the content of the input file
            with open(raw_offers, "r", encoding="utf-8") as input_file:
                content = input_file.readlines()

            # Extract lines containing valid links
            for line in content:
                match = url_pattern.search(line)

                if match:
                    links.append(match.group())

            if backup:
                # If the output file exists, rename it with a timestamp
                if os.path.exists(output_offers):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    offers_backup = f"{output_offers[:-4]}_{timestamp}.txt"
                    os.rename(output_offers, offers_backup)

            # Write the extracted links to the new output file
            with open(output_offers, "w", encoding="utf-8") as output_file:
                output_file.write("\n".join(links))
        else:
            self.logger.error(f"Input file '{raw_offers}' does not exist!")

    def is_valid_url(self, url, supported_sites):
        """
        Sprawdza, czy URL jest poprawny i należy do wspieranej domeny.
        Zwraca tuple: (czy_poprawny, strona).
        """
        pattern = re.compile(
            r"^(http|https)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$"
        )

        if not pattern.match(url):
            self.logger.error(f"Invalid URL format: {url}")
            return None

        for site in supported_sites:
            if site in url:
                return site  # Zwracamy stronę, której dotyczy oferta

        self.logger.warning(f"Unsupported site for URL: {url}")
        return None

    def load_supported_sites(self, structure_file):
        # Wczytuje obsługiwane strony z pliku sites_structure.json.
        try:
            with open(structure_file, "r", encoding="utf-8") as file:
                sites_structure = json.load(file)

            return sites_structure
        except FileNotFoundError:
            self.logger.error(f"Error: File {structure_file} not found...")

            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON in {structure_file}: {e}")

            return []
