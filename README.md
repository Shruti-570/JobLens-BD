# JobLens BD

**Understanding Bangladesh's evolving job market through data.**

JobLens BD is a modular data engineering and NLP portfolio application. It ingests job records you supply, validates and enriches them, persists them in a relational database, and presents searchable analytics. Synthetic sample records are marked DEMO and must not be interpreted as observations about the Bangladesh market.

## Features

- Interactive overview with category, location, experience, date, and employment filters.
- Searchable, paginated job explorer with CSV export.
- Skill frequency, category comparisons, experience comparisons, and co-occurrence.
- CSV and manual ingestion with Pydantic validation, normalization, deduplication, explainable skill extraction, and pipeline logs.
- Data quality checks and demo-record removal.
- SQLAlchemy schema for companies, job postings, skills, job-skill links, and pipeline runs.
- SQLite persistence by default; PostgreSQL via `DATABASE_URL`.
- Rule-based category baseline and dictionary skill extraction. No classifier has been trained or accuracy claimed: labeled training data is not bundled.

## Architecture

```mermaid
flowchart LR
  A[CSV / manual input] --> B[Validate with Pydantic]
  B --> C[Normalize and enrich]
  C --> D[Deduplicate and load]
  D --> E[(SQLite or PostgreSQL)]
  E --> F[Streamlit analytics and explorer]
  D --> G[Pipeline run log]
```

## Database design

`companies` has a unique normalized display name. `job_postings` references a company and stores source, dates, category, and demo status; source URL is unique. `skills` stores the skill dictionary, and `job_posting_skills` is a unique many-to-many bridge with cascading foreign keys. `pipeline_runs` stores counts, duration, status, and errors. See [docs/database_schema.md](docs/database_schema.md). Tables are created at startup; Alembic is listed for migration workflows but no migration revision has been generated yet.

## Setup and launch

Requires Python 3.11+.

```powershell
cd joblens_bd
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The default local SQLite database is `data/joblens.db`. To use PostgreSQL, set `DATABASE_URL` to a SQLAlchemy URL, for example `postgresql+psycopg://user:password@localhost:5432/joblens` (copy `.env.example` and set the environment variable in your shell; `.env` loading is not automatic).

## Import genuine records

Download `data/templates/jobs_template.csv`, fill the header fields, and upload it under Data Ingestion. Required fields are `title`, `company`, and a valid unique HTTP(S) `source_url`. Dates use ISO format where possible. Collection supports user-supplied CSV and manual entries; no external feed is configured by default. Optional connectors must respect public endpoint permissions and source terms.

Every seeded posting has `is_demo=true` and a `https://demo.joblens.local/` URL. The default dataset is 120 reproducible synthetic records, generated only when the database is empty. The sidebar data selector separates real-only and demo-only analytics; the application also shows a demo notice whenever demo records are in the current view.

## ETL and NLP methodology

Pydantic validates required names and HTTP(S) URLs. Transformations normalize whitespace, accept common column aliases, parse ISO-like dates, infer experience when a years expression exists, assign a transparent keyword category, and extract skills by case-insensitive dictionary matching. A row with a duplicate URL is counted as a duplicate; invalid rows are counted and their messages saved in the run log. This is a baseline, not a Bengali language model. Bengali/English mixed text works when a skill or term appears in the maintained dictionary. There is no labeled corpus, trained classifier, or model evaluation result to report.

## Limitations and next steps

- This version has startup table creation rather than a committed Alembic migration history.
- Full-text search is application-side substring matching, suitable for portfolio scale.
- The category classifier is keyword based; validate and extend it against a labeled local dataset before claiming performance.
- Source feeds and RSS/API connectors are an extension point; collection is never fabricated.
- Screenshots are not bundled; launch the application to capture your environment's live database state.

## Tests

```powershell
pytest
```

