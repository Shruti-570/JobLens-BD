from sqlalchemy import select
from database.models import Company, JobPosting, Skill, JobSkill

def load_one(session, d):
    if session.scalar(select(JobPosting.id).where(JobPosting.source_url == d["source_url"])): return "duplicate"
    company = session.scalar(select(Company).where(Company.name == d["company"]))
    if not company: company = Company(name=d["company"]); session.add(company); session.flush()
    job = JobPosting(title=d["title"], company=company, description=d["description"], location=d["location"], employment_type=d["employment_type"], experience_level=d["experience_level"], education=d["education"], salary=d["salary"], posted_date=d["posted_date"], deadline=d["deadline"], source_url=d["source_url"], source_name=d["source_name"], is_demo=d["is_demo"], category=d["category"])
    session.add(job); session.flush()
    for name in d["skills"]:
        skill = session.scalar(select(Skill).where(Skill.name == name))
        if not skill: skill = Skill(name=name); session.add(skill); session.flush()
        job.skills.append(JobSkill(skill=skill))
    return "loaded"
