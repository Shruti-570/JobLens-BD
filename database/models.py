from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Boolean, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    jobs = relationship("JobPosting", back_populates="company")

class JobPosting(Base):
    __tablename__ = "job_postings"
    __table_args__ = (UniqueConstraint("source_url", name="uq_job_source_url"), Index("ix_job_category_location", "category", "location"))
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String(160), default="Unknown", index=True)
    employment_type: Mapped[str] = mapped_column(String(80), default="Not specified")
    experience_level: Mapped[str] = mapped_column(String(80), default="Not specified")
    education: Mapped[str] = mapped_column(String(200), default="Not specified")
    salary: Mapped[str] = mapped_column(String(120), default="Not disclosed")
    posted_date: Mapped[Date | None] = mapped_column(Date, nullable=True, index=True)
    deadline: Mapped[Date | None] = mapped_column(Date, nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000), unique=True)
    source_name: Mapped[str] = mapped_column(String(120), default="Manual upload")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    category: Mapped[str] = mapped_column(String(100), default="Other", index=True)
    collected_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    company = relationship("Company", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    is_technical: Mapped[bool] = mapped_column(Boolean, default=True)
    jobs = relationship("JobSkill", back_populates="skill", cascade="all, delete-orphan")

class JobSkill(Base):
    __tablename__ = "job_posting_skills"
    __table_args__ = (UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    job = relationship("JobPosting", back_populates="skills")
    skill = relationship("Skill", back_populates="jobs")

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    status: Mapped[str] = mapped_column(String(30))
    processed: Mapped[int] = mapped_column(default=0)
    successful: Mapped[int] = mapped_column(default=0)
    rejected: Mapped[int] = mapped_column(default=0)
    duplicates: Mapped[int] = mapped_column(default=0)
    duration_seconds: Mapped[float] = mapped_column(default=0)
    details: Mapped[str] = mapped_column(Text, default="")
