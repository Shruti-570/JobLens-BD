SKILLS = ["python", "sql", "java", "c++", "javascript", "typescript", "react", "node.js", "pandas", "numpy", "scikit-learn", "machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "power bi", "tableau", "excel", "aws", "azure", "gcp", "docker", "kubernetes", "linux", "git", "postgresql", "mongodb", "fastapi", "django", "flask", "html", "css", "communication", "project management", "বাংলা", "ইংরেজি"]
CATEGORIES = {"AI/ML": ["machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "artificial intelligence"], "Data Science": ["data analyst", "data scientist", "analytics", "pandas", "power bi", "tableau"], "Software Engineering": ["software", "developer", "engineer", "backend", "frontend", "programmer"], "Networking": ["network", "system administrator", "cybersecurity", "security"], "Marketing": ["marketing", "digital marketing", "seo", "content"], "Business": ["business", "sales", "finance", "accountant"], "Administration": ["admin", "human resources", "hr", "office"]}
def extract_skills(text):
    t = str(text).casefold()
    return [s for s in SKILLS if s.casefold() in t]
def classify(text, title=""):
    t = (str(title) + " " + str(text)).casefold()
    scores = {c: sum(k in t for k in keys) for c, keys in CATEGORIES.items()}
    return max(scores, key=scores.get) if max(scores.values(), default=0) else "Other"
def extract_experience(text):
    import re
    m = re.search(r"(\d+)\s*\+?\s*(?:years?|yrs?)", str(text), re.I)
    return f"{m.group(1)}+ years" if m else "Not specified"
