import random
from datetime import date, timedelta
from pipeline.orchestrator import run_pipeline
TITLES=[("Data Analyst", "Data Science"),("Software Engineer", "Software Engineering"),("ML Engineer", "AI/ML"),("Network Engineer", "Networking"),("Digital Marketing Executive", "Marketing"),("Business Analyst", "Business"),("HR Officer", "Administration"),("Backend Developer", "Software Engineering")]
COMPANIES=["Dhaka Tech", "Bengal Digital", "Riverstone Systems", "Northstar BD", "Shapla Group", "Meghna Labs", "Bay Analytics", "Kite Solutions", "Vertex Bangladesh", "Green Delta"]
LOCATIONS=["Dhaka", "Chattogram", "Sylhet", "Remote", "Gazipur", "Rajshahi"]
STACK=["Python SQL pandas PostgreSQL", "Java Docker AWS Git", "machine learning Python scikit-learn SQL", "Linux networking cybersecurity", "Excel communication project management", "React JavaScript Node.js", "Power BI Tableau SQL Excel"]
def seed_demo(session):
    from sqlalchemy import select
    from database.models import JobPosting
    if session.scalar(select(JobPosting.id).where(JobPosting.is_demo.is_(True))): return 0
    rng=random.Random(42); rows=[]
    for i in range(120):
        title,cat=TITLES[i%len(TITLES)]; skills=STACK[i%len(STACK)]
        rows.append({"title":title,"company":COMPANIES[i%len(COMPANIES)],"description":f"We are seeking a {title} to join our team. Requirements include {skills}. Bachelor's degree preferred. {i%5+1}+ years experience. ইংরেজি ও বাংলা যোগাযোগ দক্ষতা প্রয়োজন।","location":LOCATIONS[i%len(LOCATIONS)],"employment_type":["Full-time","Contract","Internship"][i%3],"experience_level":["Entry-level","Mid-level","Senior"][i%3],"education":"Bachelor's degree","salary":"Not disclosed","posted_date":date.today()-timedelta(days=i*2),"source_url":f"https://demo.joblens.local/posting/{i+1}","source_name":"DEMO synthetic dataset","is_demo":True,"category":cat})
    return run_pipeline(session,rows)["successful"]
