###### Avaliable README.dm language versions: PL, EN

---

![Python version](https://img.shields.io/badge/python-3.12%2B-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

![Promo](/assets/images/promo.jpg)

---

###### PL

# Analiza ofert pracy

> [!CAUTION]
> Zaimportuj własne wnioski!

## Spis treści
1. [Wstęp](#wstęp)  
2. [Instrukcja obsługi](#instrukcja-obsługi)  
3. [Plany rozwoju](#plany-rozwoju)  
4. [Informacje dodatkowe](#informacje-dodatkowe)

## Wstęp
Projekt służy do **analizy** i **wizualizacji** danych o ofertach pracy w branży IT.
W obecnej wersji:
- Obsługiwane są tylko oferty z portalu [JustJoinIT](https://justjoin.it/)
- Dane mogą być pobierane zarówno z **plików JSON** (dołączonych lub pobranych z Kaggle), jak i za pomocą przygotowanej listy **linków** do ogłoszeń
> [!IMPORTANT]
> **Pliki JSON** dotyczą przedziału od **2021-10 do 2023-09**  
> Dane dostępne są w repozytorium [Kaggle](https://www.kaggle.com/datasets/jszafranqb/justjoinit-job-offers-data-2021-10-2023-09)  
> Należy je umieścić w lokalizacji `data/raw/downloaded_offers`

## Instrukcja obsługi
1. **Pobierz repozytorium**:\
```git clone https://github.com/TwojeKonto/analyzing_job_offers.git```
2. **Przejdź do lokalizacji projektu**:\
```cd analyzing_job_offers```
3. **Zainstaluj wymagane biblioteki**:\
```pip install -r requirements.txt```
4. **Wybierz źródło danych**:
   - Pobierz zestaw danych z [Kaggle](https://www.kaggle.com/datasets/jszafranqb/justjoinit-job-offers-data-2021-10-2023-09) i umieść go w folderze `data/raw/downloaded_offers`. Następnie uruchom skrypt `etl.py`, który pobierze i przetworzy pliki JSON do bazy danych
   - Stwórz plik `links.txt` w katalogu `data` i wklej linki do ofert z JustJoinIT. Kolejno uruchom `main.py` w katalogu `app`, który pobierze i przetworzy oferty do bazy danych
5. **Uruchom Jupyter Notebook**:\
Przejdź do katalogu `notebooks` i przy użyciu terminala i uruchom Jupyter Notebook za pomocą komendy `jupyter notebook`. Możesz także odpalić ręcznie plik `jupyter_notebook_launcher.bat`. Uruchomi się domyślna przeglądarka z interfejsem Jupyter – tam znajdziesz m.in. plik `job_analysis.ipynb`, który można otworzyć w celu przeglądu i wizualizacji danych. Trzeba pamiętać, że trzeba go uruchomić od samego początku aż do końca (wszystkie "cell'e")
> [!TIP]
> Jeżeli Twój plik z linkami zawiera nie tylko oferty, użyj funkcji `sort_raw_offers_file()` w klasie `Utilities` w lokalizacji `app/utilities.py`, aby odfiltrować tylko oferty pracy

## Plany rozwoju
- [ ] Obsługa wielu stron z ofertami pracy i źródeł danych (Pracuj.pl, LinkedIn, No Fluff Jobs)
- [ ] Zaprojektowanie struktur, optymalizacja oraz wdrożenie innych baz danych (PostgreSQL, MongoDB, Apache Cassandra)
- Wdrożenie agenta AI w celu:
  - [ ] rozmowy z użytkownikiem w celu wyciągnięcia wniosków z przeanalizowanych ofert pracy
  - [ ] łatwiejsze filtrowanie kluczowych wniosków z ofert
- [ ] Rozszerzenie wizualizacji o nowe funkcje i interaktywne wykresy
- [ ] Stworzenie GUI do obsługi aplikacji
- [ ] Rozbudowana analiza trendów, m.in. z wykorzystaniem machine learning (przewidywanie najgorętszych technologii)

## Informacje dodatkowe
Projekt jest rozwijany w ramach nauki i zdobywania nowych umiejętności, podczas którego musiałem zebrać wiedzę na temat:
- programowania w języku Python
- Web Scrapingu
- ETL (Extract, Transform, Load)
- baz danych (SQLite)
- analizy oraz wizualizacji danych
- testów

---

###### EN

# Job analysis

> [!CAUTION]
> Import your own conclusions!

## Table of contents
1. [Introduction](#introduction)  
2. [User manual](#user-manual)  
3. [Development plans](#development-plans)  
4. [Additional information](#additional-information )

## Introduction
The project is used for **analysis** and **visualization** of job offer data in the IT industry.
In the current version:
- Only listings from [JustJoinIT](https://justjoin.it/) are supported
- Data can be retrieved both from **JSON files** (attached or downloaded from Kaggle) and by using a prepared list of **links** to ads
> [!IMPORTANT]
> The **JSON files** are for the period from **2021-10 to 2023-09**.  
> The data is available in the repository [Kaggle](https://www.kaggle.com/datasets/jszafranqb/justjoinit-job-offers-data-2021-10-2023-09)  
> They should be placed in the location `data/raw/downloaded_offers`.

## User Manual
1. **Download the repository**:\
```git clone https://github.com/TwojeKonto/analyzing_job_offers.git```
2. **Go to project location**:\
```cd analyzing_job_offers```
3. **Install the required libraries**:\
```pip install -r requirements.txt```
4. **Select a data source**:
   - Download the dataset from [Kaggle](https://www.kaggle.com/datasets/jszafranqb/justjoinit-job-offers-data-2021-10-2023-09) and place them in the folder `data/raw/downloaded_offers`. Then run the script `etl.py`, which will download and parse the JSON files into the database
   - Create a file `links.txt` in folder `data` and paste links to your listings from JustJoinIT. Next, run `main.py` in the `app` directory, which will download and process the listings to the database
5. **Launch Jupyter Notebook**:\
Navigate to the `notebooks` directory and using a terminal and launch Jupyter Notebook using the `jupyter notebook` command. You can also fire up the `jupyter_notebook_launcher.bat` file manually. It will launch the default browser with Jupyter interface - there you will find, among other things, the `job_analysis.ipynb` file, which you can open to review and visualize the data. Keep in mind that you need to run it from the very beginning all the way to the end (all “cells”)
> [!TIP]
> If your link file contains more than just listings, use the `sort_raw_offers_file()` function in the `Utilities` class in the `app/utilities.py` location to filter out only job listings

## Development plans
- [ ] Supporting multiple job sites and data sources (Pracuj.pl, LinkedIn, No Fluff Jobs)
- [ ] Design of structures, optimization and implementation of other databases (PostgreSQL, MongoDB, Apache Cassandra)
- Implementation of AI agent to:
  - [ ] talk to users to draw conclusions from analyzed job offers
  - [ ] easier filtering of key findings from offers
- [ ] Enhance visualization with new features and interactive charts
- [ ] Creation of a GUI to operate the application
- [ ] Expanded trend analysis, including using machine learning (predicting the hottest technologies)

## Additional information
The project is being developed as a part of learning and acquiring new skills, during which I had to gather knowledge about:
- Python programming
- Web Scraping
- ETL (Extract, Transform, Load)
- databases (SQLite)
- analysis and data visualization
- tests
