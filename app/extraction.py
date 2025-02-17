import json
import os
import re

import requests
from bs4 import BeautifulSoup


def find_original_url(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Szukamy <link rel="canonical">
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.has_attr("href"):
        return canonical["href"]

    # Szukamy <meta property="og:url">
    og_url = soup.find("meta", property="og:url")
    if og_url and og_url.has_attr("content"):
        return og_url["content"]

    # Szukamy w komentarzach (np. 'Saved from')
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and "Saved from" in text):
        url = comment.split("Saved from")[-1].strip()
        if url.startswith("http"):
            return url

    return "Nie znaleziono oryginalnego URL-a."


class Extraction:
    def __init__(self, logger, db, sites_structure, downloaded_offers):
        self.logger = logger
        self.db = db
        self.sites_structure = sites_structure
        self.downloaded_offers = downloaded_offers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                          "like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        self.tech_levels = {
            "nice to have": 1,
            "junior": 2,
            "regular": 3,
            "advanced": 4,
            "master": 5
        }

    def save_file_locally(self, html):
        """A function to download jobs locally."""
        # Check if the folder exists, if not, create it
        if not os.path.exists(self.downloaded_offers):
            os.makedirs(self.downloaded_offers)
            self.logger.info(f"Directory {self.downloaded_offers} created.")

        # Give a secure title for the file
        title = html.title.string if html.title else "no_title"

        safe_title = (
            "".join(c for c in title if c.isalnum() or c in " _-")  # Only allowed characters
            .replace(" ", "_")  # Convert spaces to underscores
            .strip()  # Removal of unnecessary characters
            .lower()
        )

        # File save path
        file_path = os.path.join(self.downloaded_offers, f"{safe_title}.html")

        # Saving the contents of the page to a file
        if os.path.exists(file_path):
            self.logger.info(f"The file {safe_title}.html already exists. Skipping download.")
        else:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(html.prettify())
                self.logger.info(f"File {safe_title}.html saved successfully.")
            except Exception as e:
                self.logger.error(f"Error while saving file {safe_title}.html: {e}")

    def link_extraction(self, url, offer_site):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Page download error for URL {url}: {e}")
            return

        try:
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            self.logger.error(f"Unexpected error for URL {url}: {e}")
            return

        self.save_file_locally(soup)

        job_offer_data = {
            "title": None,
            "company": None,
            "location": None,
            "category": None,
            "position": None,
            "date_add": None,
            "salary": None,
            "experience": None,
            "employment": None,
            "operating_mode": None,
            "tech_stack": None,
            "link": url,
            "source": "url"
        }

        try:
            for column, selector in self.sites_structure.get(offer_site, {}).items():
                try:
                    tag_name = selector.get("tag")
                    class_name = selector.get("class")

                    if column == "title":
                        job_offer_data["title"] = soup.find(tag_name, class_=class_name).find("h1").text.strip()
                    if column == "date_add":
                        match = re.search(r'\\"publishedAt\\":\\"(.*?)\\"', response.text)

                        if match:
                            published_at = match.group(1)  # Pobieramy tylko datę
                            formatted_date = published_at.replace("T", " ").replace("Z", "")
                            job_offer_data["date_add"] = formatted_date
                    elif column == "salary":
                        salary_tag_name = selector.get("salary_tag")
                        salary_class_name = selector.get("salary_class")
                        contract_tag_name = selector.get("contract_tag")
                        contract_class_name = selector.get("contract_class")
                        elements = soup.find_all(tag_name, class_=class_name)

                        existing_salary = {}

                        for element in elements:
                            salary = element.find(salary_tag_name, class_=salary_class_name).text.strip()
                            contract = element.find(contract_tag_name, class_=contract_class_name).text.strip()

                            salary_pattern = r'(\d[\d\s]*\d)\s*-\s*(\d[\d\s]*\d)\s*(\w+)'
                            salary_match = re.match(salary_pattern, salary)

                            if not salary_match:
                                raise ValueError("Format wartości 'salary' jest nieprawidłowy")

                            min_salary = salary_match.group(1).replace(" ", "")
                            max_salary = salary_match.group(2).replace(" ", "")
                            currency = salary_match.group(3)

                            contract = contract.strip()
                            contract_pattern = r'-\s*(\w+)$'
                            contract_match = re.search(contract_pattern, contract)

                            if not contract_match:
                                raise ValueError("Format wartości 'contract' jest nieprawidłowy")

                            contract_type = contract_match.group(1)

                            # return min_salary, max_salary, currency, contract_type
                            existing_salary[contract_type] = {
                                'from': min_salary,
                                'to': max_salary,
                                'currency': currency
                            }

                        job_offer_data["salary"] = json.dumps(existing_salary).lower()
                    elif column == "details":
                        child_tag_name = selector.get("child_tag")
                        child_class_name = selector.get("child_class")

                        elements = soup.find_all(tag_name, class_=class_name)

                        for element in elements:
                            element_text = element.text.strip()
                            elements_value = element.parent.find(child_tag_name, class_=child_class_name).text.strip()

                            if element_text == "Type of work":
                                job_offer_data["type"] = elements_value
                            if element_text == "Experience":
                                job_offer_data["experience"] = elements_value.lower()
                            elif element_text == "Employment Type":
                                job_offer_data["employment"] = elements_value.lower()
                            elif element_text == "Operating mode":
                                job_offer_data["operating_mode"] = elements_value.lower()
                    elif column == "technology_level":
                        technology_tag_name = selector.get("technology_tag")
                        technology_tag_class = selector.get("technology_class")
                        level_tag_name = selector.get("level_tag")
                        level_class_name = selector.get("level_class")

                        technology_levels = {}

                        elements = soup.find_all(tag_name, class_=class_name)

                        for element in elements:
                            technology = element.find(technology_tag_name, class_=technology_tag_class).text.strip()
                            level = element.find(level_tag_name, class_=level_class_name).text.strip()

                            technology_levels[technology] = self.tech_levels.get(level, 0)

                        job_offer_data["tech_stack"] = json.dumps(technology_levels)
                    elif column == "location" or column == "category":
                        if job_offer_data[column] is None:
                            job_offer_data[column] = soup.find(tag_name, class_=class_name).text.strip().lower()
                    else:
                        if job_offer_data[column] is None:
                            job_offer_data[column] = soup.find(tag_name, class_=class_name).text.strip()

                except AttributeError as e:
                    self.logger.error(f"Attribute error while extracting data '{column}' from file {url}: {e}")

            self.db.insert_job_offer(job_offer_data)
        except Exception as e:
            self.logger.error(f"Unexpected error while extracting data: {e}")

    def file_extraction(self, file_path, offer_site):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
        except Exception as e:
            self.logger.error(f"Unexpected error for file {file_path}: {e}")
            return

        job_offer_data = {
            "title": None,
            "company": None,
            "location": None,
            "category": None,
            "position": None,
            "date_add": None,
            "salary": None,
            "experience": None,
            "employment": None,
            "operating_mode": None,
            "tech_stack": None,
            "link": find_original_url(file_path),
            "source": "file"
        }

        try:
            for column, selector in self.sites_structure.get(offer_site, {}).items():
                try:
                    tag_name = selector.get("tag")
                    class_name = selector.get("class")

                    if column == "title":
                        job_offer_data["title"] = soup.find(tag_name, class_=class_name).find("h1").text.strip()
                    if column == "date_add":
                        with open(file_path, "r", encoding="utf-8") as file:
                            response_text = file.read()

                        match = re.search(r'\\"publishedAt\\":\\"(.*?)\\"', response_text)

                        if match:
                            published_at = match.group(1)  # Pobieramy tylko datę
                            formatted_date = published_at.replace("T", " ").replace("Z", "")
                            job_offer_data["date_add"] = formatted_date
                    elif column == "salary":
                        salary_tag_name = selector.get("salary_tag")
                        salary_class_name = selector.get("salary_class")
                        contract_tag_name = selector.get("contract_tag")
                        contract_class_name = selector.get("contract_class")
                        elements = soup.find_all(tag_name, class_=class_name)

                        existing_salary = {}

                        for element in elements:
                            salary = element.find(salary_tag_name, class_=salary_class_name).text.strip()
                            contract = element.find(contract_tag_name, class_=contract_class_name).text.strip()

                            salary_pattern = r'(\d[\d\s]*\d)\s*-\s*(\d[\d\s]*\d)\s*(\w+)'
                            salary_match = re.match(salary_pattern, salary)

                            if not salary_match:
                                raise ValueError("Format wartości 'salary' jest nieprawidłowy")

                            min_salary = salary_match.group(1).replace(" ", "")
                            max_salary = salary_match.group(2).replace(" ", "")
                            currency = salary_match.group(3)

                            contract = contract.strip()
                            contract_pattern = r'-\s*(\w+)$'
                            contract_match = re.search(contract_pattern, contract)

                            if not contract_match:
                                raise ValueError("Format wartości 'contract' jest nieprawidłowy")

                            contract_type = contract_match.group(1)

                            # return min_salary, max_salary, currency, contract_type
                            existing_salary[contract_type] = {
                                'from': min_salary,
                                'to': max_salary,
                                'currency': currency
                            }

                        job_offer_data["salary"] = json.dumps(existing_salary).lower()
                    elif column == "details":
                        child_tag_name = selector.get("child_tag")
                        child_class_name = selector.get("child_class")

                        elements = soup.find_all(tag_name, class_=class_name)

                        for element in elements:
                            element_text = element.text.strip()
                            elements_value = element.parent.find(child_tag_name, class_=child_class_name).text.strip()

                            if element_text == "Type of work":
                                job_offer_data["type"] = elements_value
                            if element_text == "Experience":
                                job_offer_data["experience"] = elements_value.lower()
                            elif element_text == "Employment Type":
                                job_offer_data["employment"] = elements_value.lower()
                            elif element_text == "Operating mode":
                                job_offer_data["operating_mode"] = elements_value.lower()
                    elif column == "technology_level":
                        technology_tag_name = selector.get("technology_tag")
                        technology_tag_class = selector.get("technology_class")
                        level_tag_name = selector.get("level_tag")
                        level_class_name = selector.get("level_class")

                        technology_levels = {}

                        elements = soup.find_all(tag_name, class_=class_name)

                        for element in elements:
                            technology = element.find(technology_tag_name, class_=technology_tag_class).text.strip()
                            level = element.find(level_tag_name, class_=level_class_name).text.strip()

                            technology_levels[technology] = self.tech_levels.get(level, 0)

                        job_offer_data["tech_stack"] = json.dumps(technology_levels)
                    elif column == "location" or column == "category":
                        if job_offer_data[column] is None:
                            job_offer_data[column] = soup.find(tag_name, class_=class_name).text.strip().lower()
                    else:
                        if job_offer_data[column] is None:
                            job_offer_data[column] = soup.find(tag_name, class_=class_name).text.strip()

                except AttributeError as e:
                    self.logger.error(f"Attribute error while extracting data '{column}' from file {file_path}: {e}")

            self.db.insert_job_offer(job_offer_data)

        except Exception as e:
            self.logger.error(f"Unexpected error while extracting data from file {file_path}: {e}")

    def text_extraction(self):
        pass

    def site_extraction(self, site):
        pass
