"""
src/agents/nba_engine.py
Next Best Action (NBA) multi-agent orchestrator.
Coordinates Skill Coach, Placement Advisor, and Interview Mentor.
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Any

from src.agents.skill_coach      import SkillCoachAgent
from src.agents.placement_advisor import PlacementAdvisorAgent
from src.agents.interview_mentor  import InterviewMentorAgent


class NBAEngine:
    """
    Orchestrates three specialised agents and merges their outputs
    into a unified action plan and executive summary.
    """

    def __init__(self) -> None:
        self.skill_coach       = SkillCoachAgent()
        self.placement_advisor = PlacementAdvisorAgent()
        self.interview_mentor  = InterviewMentorAgent()

    def run(
        self,
        shap_drivers: List[Tuple[str, float]],
        risk_level:   str,
        salary:       float,
        time_to_job:  float,
        sample:       Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Parameters
        ----------
        shap_drivers : [(feature, shap_value), ...]
        risk_level   : "High" | "Medium" | "Low"
        salary       : predicted salary in LPA
        time_to_job  : predicted months to placement
        sample       : raw student input dict

        Returns
        -------
        dict with keys:
            skill_coach, placement_advisor, interview_mentor,
            top_actions, improvement_roadmap
        """
        cgpa          = float(sample.get("cgpa", 7.0))
        skill_score   = float(sample.get("skills", 0.3))
        n_internships = int(sample.get("internship_count", sample.get("internship", 0)))
        interviews    = int(sample.get("interviews", 0))
        current_skills= list(sample.get("skill_list", []))

        # ── Run agents ────────────────────────────────────────────────────────
        skill_out = self.skill_coach.run(
            shap_drivers=shap_drivers,
            skill_score=skill_score,
            current_skills=current_skills,
            risk_level=risk_level,
        )

        advisor_out = self.placement_advisor.run(
            shap_drivers=shap_drivers,
            risk_level=risk_level,
            cgpa=cgpa,
            skill_score=skill_score,
            n_internships=n_internships,
            time_to_job=time_to_job,
            salary_estimate=salary,
        )

        mentor_out = self.interview_mentor.run(
            shap_drivers=shap_drivers,
            risk_level=risk_level,
            interviews_completed=interviews,
            cgpa=cgpa,
            skill_score=skill_score,
        )

        # ── Synthesise top-3 cross-agent actions ──────────────────────────────
        top_actions: List[str] = []

        # Always include one action from each agent
        if skill_out["action_items"]:
            top_actions.append(f"[Skill]       {skill_out['action_items'][0]}")
        if advisor_out["application_strategy"]:
            top_actions.append(f"[Placement]   {advisor_out['application_strategy'][0]}")
        if mentor_out["critical_gaps"]:
            top_actions.append(f"[Interview]   {mentor_out['critical_gaps'][0]}")

        # ── Improvement roadmap (milestone-based) ────────────────────────────
        roadmap = _build_roadmap(
            risk_level, skill_out, advisor_out, mentor_out, time_to_job
        )

        return {
            "skill_coach":        skill_out,
            "placement_advisor":  advisor_out,
            "interview_mentor":   mentor_out,
            "top_actions":        top_actions,
            "improvement_roadmap": roadmap,
        }


# ── Roadmap helper ────────────────────────────────────────────────────────────

def _build_roadmap(
    risk_level: str,
    skill_out: Dict,
    advisor_out: Dict,
    mentor_out: Dict,
    time_to_job: float,
) -> List[Dict[str, str]]:
    """Build a timeline milestone list."""
    weeks = mentor_out["mock_schedule"]["weeks"]

    milestones = [
        {
            "phase":    "Week 1–2",
            "focus":    "Skill & Profile Sprint",
            "actions":  (
                f"Enrol in {skill_out['certifications'][0]['certification'] if skill_out['certifications'] else 'a relevant course'}. "
                "Update LinkedIn, GitHub, and resume."
            ),
        },
        {
            "phase":    f"Week 3–{weeks // 2 + 2}",
            "focus":    "Interview Prep",
            "actions":  (
                f"Solve {mentor_out['mock_schedule']['dsa_daily_problems']} DSA problems/day. "
                f"Complete {mentor_out['mock_schedule']['mocks_per_week']} mock interviews/week."
            ),
        },
        {
            "phase":    f"Week {weeks // 2 + 3}–{weeks + 2}",
            "focus":    "Active Applications",
            "actions":  (
                f"Apply to {advisor_out['applications_per_week']} companies/week targeting {advisor_out['target_tier']}. "
                "Track applications in a spreadsheet."
            ),
        },
        {
            "phase":    f"Month {int(time_to_job)}",
            "focus":    "Offer & Negotiation",
            "actions":  advisor_out["salary_negotiation"],
        },
    ]
    return milestones
