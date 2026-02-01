-- Create tables for the Market Research Database

CREATE TABLE IF NOT EXISTS studies (
    id SERIAL PRIMARY KEY,
    study_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS brands (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(255),
    study_id INTEGER REFERENCES studies(id)
);

CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    metric_code VARCHAR(255),
    metric_label TEXT,
    study_id INTEGER REFERENCES studies(id)
);

-- Responses table: Optimized for flexible storage (long format is often better for analysis, 
-- but wide is common for SPSS. Here we assume a flexible structure or mapping).
-- Ideally, raw SPSS data is dumped into a table per study, or a massive 'responses' table.
-- For this schema, we'll assume a 'responses' table that links respondent to brand/metric values.
-- Or more simply for this MVP, we store the raw dump in a dynamic table or keep it as:
CREATE TABLE IF NOT EXISTS raw_responses (
    id SERIAL PRIMARY KEY,
    study_id INTEGER REFERENCES studies(id),
    respondent_id VARCHAR(255),
    variable_name VARCHAR(255),
    value_code FLOAT,
    value_label TEXT
);

CREATE TABLE IF NOT EXISTS data_checks (
    id SERIAL PRIMARY KEY,
    study_id INTEGER REFERENCES studies(id),
    check_category VARCHAR(100), -- e.g. 'Time frame', 'Missing Data'
    check_item VARCHAR(255),     -- e.g. 'Week No.', 'Familiarity'
    status VARCHAR(50),          -- 'Pass', 'Fail', 'Warning'
    details TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS preanalysis_results (
    id SERIAL PRIMARY KEY,
    study_id INTEGER REFERENCES studies(id),
    brand_id INTEGER REFERENCES brands(id),
    metric_id INTEGER REFERENCES metrics(id),
    mean_score FLOAT
);

CREATE TABLE IF NOT EXISTS correlations (
    id SERIAL PRIMARY KEY,
    study_id INTEGER REFERENCES studies(id),
    brand_id INTEGER REFERENCES brands(id),
    metric_a_id INTEGER REFERENCES metrics(id),
    metric_b_id INTEGER REFERENCES metrics(id),
    score FLOAT
);
