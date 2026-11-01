from datetime import date
import re
from nlp.skill_extraction import extract_skills, classify, extract_experience

def clean(s): return re.sub(r"\s+", " ", str(s or "")).strip()
def transform(row):
    d = {str(k).strip().lower().replace(" ", "_"): clean(v) for k,v in row.items()}
    d["title"] = d.get("title", d.get("job_title", ""))
    d["company"] = d.get("company", d.get("company_name", ""))
    d["description"] = d.get("description", d.get("job_description", ""))
    d["location"] = d.get("location") or "Unknown"
    d["employment_type"] = d.get("employment_type") or "Not specified"
    d["experience_level"] = d.get("experience_level") or extract_experience(d["description"])
    d["education"] = d.get("education") or "Not specified"
    d["salary"] = d.get("salary") or "Not disclosed"
    d["source_url"] = d.get("source_url", "")
    d["source_name"] = d.get("source_name") or "CSV upload"
    d["is_demo"] = str(d.get("is_demo", "false")).lower() == "true"
    for f in ("posted_date", "deadline"):
        if d.get(f):
            try: d[f] = date.fromisoformat(d[f][:10])
            except ValueError: d[f] = None
        else: d[f] = None
    d["category"] = d.get("category") or classify(d["description"], d["title"])
    d["skills"] = extract_skills(d["title"] + " " + d["description"])
    return d
