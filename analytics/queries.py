from sqlalchemy import select, func
from database.models import JobPosting, Company, Skill, JobSkill
def jobs_query(session): return session.scalars(select(JobPosting).order_by(JobPosting.posted_date.desc().nullslast(), JobPosting.id.desc())).all()
def summary(session):
    return {"jobs":session.scalar(select(func.count(JobPosting.id))) or 0,"companies":session.scalar(select(func.count(Company.id))) or 0}
