# Schema notes

- `companies(id, name UNIQUE)` — one company to many postings.
- `job_postings(id, company_id FK, title, description, location, employment_type, experience_level, education, salary, posted_date, deadline, source_url UNIQUE, source_name, is_demo, category, collected_at)`.
- `skills(id, name UNIQUE, is_technical)` — canonical dictionary labels.
- `job_posting_skills(job_id FK, skill_id FK, UNIQUE(job_id, skill_id))` — many-to-many association; cascading deletion.
- `pipeline_runs(id, started_at, status, processed, successful, rejected, duplicates, duration_seconds, details)`.

Indexes support company, title, category, location, source URL, demo flag and posting date lookups. ER: Company 1—N JobPosting; JobPosting N—M Skill through JobPostingSkill.
