###### Avaliable README.dm language versions: PL, EN

---

###### PL

![Python version](https://img.shields.io/badge/python-3.12%2B-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

# Analiza ofert pracy

> [!CAUTION]
> Zaimportuj własne wnioski!

![Promo](docs/images/promo.png)

---

## Spis treści
1. [Wstęp](#wstęp)  
2. [Instrukcja obsługi](#instrukcja-obsługi)  
3. [Plany rozwoju](#plany-rozwoju)  
4. [Informacje dodatkowe](#informacje-dodatkowe)

## Wstęp
Projekt służy do **analizy** i **wizualizacji** danych o ofertach pracy w branży IT.
W obecnej wersji:
- Obsługiwane są głównie oferty z portalu [JustJoinIT](https://justjoin.it/)
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
Przejdź do katalogu `notebooks` przy użyciu terminala i uruchom Jupyter Notebook za pomocą komendy `jupyter notebook`. Uruchomi się domyślna przeglądarka z interfejsem Jupyter – tam znajdziesz m.in. plik `job_analysis.ipynb`, który można otworzyć w celu przeglądu i wizualizacji danych. Trzeba pamiętać, że trzeba go uruchomić od samego początku aż do końca (wszystkie "cell'e")
> [!TIP]
> Jeżeli Twój plik z linkami zawiera nie tylko oferty, użyj funkcji `sort_raw_offers_file()` w klasie `Utilities` w lokalizacji `app/utilities.py`, aby odfiltrować tylko oferty pracy

## Plany rozwoju
- Obsługa wielu stron z ofertami pracy i źródeł danych (Pracuj.pl, LinkedIn, No Fluff Jobs)
- Zaprojektowanie struktur, optymalizacja oraz wdrożenie innych baz danych (PostgreSQL, MongoDB, Apache Cassandra)
- Wdrożenie agenta AI w celu:
  - rozmowy z użytkownikiem w celu wyciągnięcia wniosków z przeanalizowanych ofert pracy
  - łatwiejsze filtrowanie kluczowych wniosków z ofert
- Rozszerzenie wizualizacji o nowe funkcje i interaktywne wykresy
- Stworzenie GUI do obsługi aplikacji
- Rozbudowana analiza trendów, m.in. z wykorzystaniem machine learning (przewidywanie najgorętszych technologii)

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

# Analyzing job offers

## Introduction
This project is about analyzing job offers.
The goal is to extract information from job offers and to analyze the job market.
The project is divided into two parts: the first part is about extracting information from job offers and the second part is about analyzing the job market. The project is based on the data from the job offers website [Indeed](https://www.indeed.com/). The project is written in Python and uses the following libraries: [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/), [matplotlib](https://matplotlib.org/), [seaborn](https://seaborn.pydata.org/), [scikit-learn](https://scikit-learn.org/), [nltk](https://www.nltk.org/), [wordcloud](