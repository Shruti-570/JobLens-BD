import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date
from urllib.parse import urlparse
class JobRecord(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=2, max_length=300)
    company: str = Field(min_length=1, max_length=200)
    description: str = ""
    location: str = "Unknown"
    employment_type: str = "Not specified"
    experience_level: str = "Not specified"
    education: str = "Not specified"
    salary: str = "Not disclosed"
    posted_date: date | None = None
    deadline: date | None = None
    source_url: str = Field(min_length=8, max_length=1000)
    source_name: str = "CSV upload"
    is_demo: bool = False
    @field_validator("source_url")
    @classmethod
    def valid_url(cls, v):
        if urlparse(v).scheme not in ("http", "https") or not urlparse(v).netloc: raise ValueError("source_url must be an http(s) URL")
        return v

def parse_csv(file):
    return pd.read_csv(file).fillna("")
