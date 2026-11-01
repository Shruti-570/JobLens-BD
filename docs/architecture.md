# Architecture notes

Streamlit is the presentation and interaction layer. `ingestion.validation` parses source data and validates records. `pipeline.transform` normalizes, classifies, infers experience and extracts skills. `pipeline.load` performs idempotency checks and normalized relational writes. `pipeline.orchestrator` records outcomes including row-level errors. SQLAlchemy abstracts SQLite/PostgreSQL. Analytics are derived from database rows at request time.
