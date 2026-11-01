from pipeline.transform import transform
from nlp.skill_extraction import extract_skills, classify, extract_experience
from ingestion.validation import JobRecord
import pytest

def test_skill_extraction_mixed_language():
    skills=extract_skills("We need Python and SQL. বাংলা যোগাযোগ দক্ষতা প্রয়োজন")
    assert "python" in skills and "sql" in skills and "বাংলা" in skills

def test_rule_classifier(): assert classify("Build machine learning models", "ML Engineer")=="AI/ML"
def test_experience(): assert extract_experience("3+ years experience") == "3+ years"
def test_transform_normalizes_and_extracts():
    d=transform({"job title":"Data Analyst","company name":"Acme","job description":"Use pandas and SQL, 2 years experience","source url":"https://example.com/jobs/1"})
    assert d["title"]=="Data Analyst" and "sql" in d["skills"] and d["experience_level"]=="2+ years"
def test_rejects_invalid_url():
    with pytest.raises(Exception): JobRecord(title="Engineer",company="Acme",source_url="not a url")
