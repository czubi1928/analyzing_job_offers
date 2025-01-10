-- database structure
CREATE TABLE IF NOT EXISTS job_offers
(
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    title          TEXT NOT NULL,
    company        TEXT NOT NULL,
    location       TEXT,
    category       TEXT NOT NULL,
    --position       TEXT,
    date_add       TEXT,
    salary         BLOB,
    experience     TEXT NOT NULL,
    employment     TEXT NOT NULL,
    operating_mode TEXT NOT NULL,
    tech_stack     BLOB,
    link           TEXT UNIQUE,
    source         TEXT NOT NULL,
    --input_source     TEXT NOT NULL,
    UNIQUE (title, company, location)
);

CREATE INDEX idx_offers_category ON job_offers (category);

CREATE INDEX idx_offers_location ON job_offers (location);

CREATE INDEX idx_offers_experience ON job_offers (experience);

CREATE INDEX idx_offers_date_add ON job_offers (date_add);

CREATE UNIQUE INDEX job_offers_uindex
    ON job_offers (title, company, category, location, source, link, date_add, operating_mode);
