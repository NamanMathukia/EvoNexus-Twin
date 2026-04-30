"""
src/data/schema.py
Pydantic data contracts for the ENT system.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class TemporalTriplet(BaseModel):
    event_type: str          # "skill_acquired" | "internship" | "applied" | "placed"
    entity: str              # skill name, company name, etc.
    timestamp: float         # months since enrollment start (0-48)


class TrajectoryStep(BaseModel):
    semester: int
    cgpa: float
    skills_this_sem: List[str]
    cum_skill_count: int
    has_internship: bool
    internship_company: Optional[str] = None
    market_demand: float
    engagement_score: float
    portal_activity: float


class InternshipRecord(BaseModel):
    company: str
    role: str
    duration_months: int
    semester: int
    quality: float           # 0-1
    tier: str                # "top" | "mid" | "startup"


class StudentProfile(BaseModel):
    student_id: str
    trajectory: List[TrajectoryStep]
    triplets: List[TemporalTriplet]
    internships: List[InternshipRecord]
    final_skills: List[str]
    final_cgpa: float
    skill_score: float       # 0-1 normalised
    n_internships: int
    avg_internship_quality: float
    portal_activity: float
    resume_updates: int
    interviews: int
    placed: bool
    months_to_placement: float
    salary: float
    risk_level: str          # "High" | "Medium" | "Low"
    placement_score: float
