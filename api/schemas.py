"""
api/schemas.py
Pydantic request/response models for the FastAPI backend.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class TextEvaluateRequest(BaseModel):
    resume_text: str = Field(..., description="Raw text of the candidate's resume/profile")


class StudentInput(BaseModel):
    cgpa:                 float = Field(7.5,  ge=0.0, le=10.0, description="CGPA (0-10)")
    skills:               float = Field(0.4,  ge=0.0, le=1.0,  description="Normalised skill breadth (0-1)")
    internship:           int   = Field(1,    ge=0,   le=1,    description="Has done internship? (0/1)")
    internship_count:     int   = Field(1,    ge=0,            description="Total internships completed")
    internship_quality:   float = Field(0.6,  ge=0.0, le=1.0,  description="Avg internship quality (0-1)")
    academic_consistency: float = Field(0.75, ge=0.0, le=1.0,  description="Academic consistency (0-1)")
    portal_activity:      float = Field(0.5,  ge=0.0, le=1.0,  description="Career portal engagement (0-1)")
    resume_updates:       int   = Field(2,    ge=0,            description="No. of resume updates")
    interviews:           int   = Field(3,    ge=0,            description="Mock interviews completed")
    skill_demand_score:   float = Field(0.7,  ge=0.0, le=1.0,  description="Avg demand score of skills")
    skill_list:           List[str] = Field(default_factory=list,
                                            description="List of skill names (see generator.SKILL_VOCABULARY)")
    market_demand:        float = Field(0.7,  ge=0.0, le=1.0,  description="Current job market demand index")

    model_config = {"json_schema_extra": {"example": {
        "cgpa": 7.8, "skills": 0.55, "internship": 1, "internship_count": 2,
        "internship_quality": 0.70, "academic_consistency": 0.80,
        "portal_activity": 0.65, "resume_updates": 3, "interviews": 5,
        "skill_demand_score": 0.78,
        "skill_list": ["python", "sql", "machine_learning", "docker", "git"],
        "market_demand": 0.75,
    }}}


class AgentOutput(BaseModel):
    skill_coach:        Dict[str, Any]
    placement_advisor:  Dict[str, Any]
    interview_mentor:   Dict[str, Any]
    top_actions:        List[str]
    improvement_roadmap: List[Dict[str, str]]


class PredictionOutput(BaseModel):
    risk:         str   = Field(..., description="High | Medium | Low")
    salary:       float = Field(..., description="Predicted salary in LPA")
    time_to_job:  float = Field(..., description="Predicted months to placement")
    lstm_prob:    float = Field(..., description="LSTM trajectory placement probability")
    set_net_prob: float = Field(..., description="SetNet skill placement probability")
    drivers:      List[Tuple[str, float]] = Field(..., description="Top SHAP drivers")
    interactions: List[Tuple[str, float]] = Field(..., description="Top SHAP interactions")
    actions:      AgentOutput
    summary:      str   = Field(..., description="Executive summary text")


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
