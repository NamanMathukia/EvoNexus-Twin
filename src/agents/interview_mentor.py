"""
src/agents/interview_mentor.py
Interview Mentor Agent — generates structured interview prep plan.
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Any


PREP_RESOURCES: Dict[str, List[str]] = {
    "DSA": [
        "LeetCode Top 150 Interview Questions",
        "NeetCode.io structured roadmap",
        "Striver's SDE Sheet (180 problems)",
    ],
    "System Design": [
        "Grokking System Design (Educative)",
        "ByteByteGo newsletter + YouTube",
        "Designing Data-Intensive Applications (book)",
    ],
    "HR & Behavioural": [
        "STAR method framework for all behavioural answers",
        "Glassdoor company-specific interview Q&As",
        "ChatGPT mock HR interview (self-practice)",
    ],
    "Domain": [
        "Role-specific: ML → Kaggle case studies",
        "Role-specific: SDE → OS/DBMS/CN fundamentals",
        "Role-specific: Analytics → SQL + case interviews",
    ],
}

MOCK_SCHEDULE: Dict[str, Dict] = {
    "High":   {"mocks_per_week": 5, "dsa_daily_problems": 5, "weeks": 8},
    "Medium": {"mocks_per_week": 3, "dsa_daily_problems": 3, "weeks": 5},
    "Low":    {"mocks_per_week": 1, "dsa_daily_problems": 2, "weeks": 3},
}


class InterviewMentorAgent:
    """
    Analyses interview readiness signals and generates a structured
    mock-interview schedule and preparation plan.
    """

    def run(
        self,
        shap_drivers: List[Tuple[str, float]],
        risk_level: str,
        interviews_completed: int,
        cgpa: float,
        skill_score: float,
    ) -> Dict[str, Any]:
        """
        Returns
        -------
        dict with keys: readiness_score, weekly_plan, resources,
                        mock_schedule, critical_gaps
        """
        schedule = MOCK_SCHEDULE.get(risk_level, MOCK_SCHEDULE["Medium"])

        # Readiness score (0-100)
        readiness = min(100, int(
            30 * (cgpa / 10.0)
            + 30 * skill_score
            + 20 * min(interviews_completed / 8.0, 1.0)
            + 20 * (1.0 if risk_level == "Low" else 0.5 if risk_level == "Medium" else 0.1)
        ))

        # Identify interview-related SHAP gaps
        interview_shap_gap = any("interview" in f and v > 0 for f, v in shap_drivers)

        critical_gaps: List[str] = []
        if interview_shap_gap or interviews_completed < 3:
            critical_gaps.append(f"Low mock interview count ({interviews_completed}). Schedule 5 mocks this week.")
        if cgpa < 6.5:
            critical_gaps.append("CGPA below cut-off for many companies. Highlight projects + internships strongly.")
        if skill_score < 0.3:
            critical_gaps.append("Skill breadth is a concern — focus DSA + 1 domain skill immediately.")

        weekly_plan = [
            f"Mon–Fri : {schedule['dsa_daily_problems']} LeetCode problems/day (Easy→Medium→Hard progression)",
            f"Sat     : {schedule['mocks_per_week']} mock technical interview (Pramp / interviewing.io)",
            "Sun     : Review weak areas + 1 system-design walkthrough",
            f"Duration: {schedule['weeks']} weeks intensive prep plan",
        ]

        return {
            "readiness_score": readiness,
            "readiness_label": (
                "High" if readiness >= 70 else "Moderate" if readiness >= 45 else "Low"
            ),
            "weekly_plan":     weekly_plan,
            "resources":       PREP_RESOURCES,
            "mock_schedule":   schedule,
            "critical_gaps":   critical_gaps if critical_gaps else ["No critical gaps — maintain pace"],
            "platforms":       ["Pramp.com", "Interviewing.io", "LeetCode Discuss", "NeetCode.io"],
        }
