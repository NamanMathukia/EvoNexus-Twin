"""
src/agents/nba_engine.py
Next Best Action (NBA) multi-agent orchestrator.
Coordinates Skill Coach, Placement Advisor, and Interview Mentor.
"""
from __future__ import annotations

import os
import json
import math
import requests
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

        # ── Improvement roadmap (LLM-Generated) ──────────────────────────────
        roadmap = _build_roadmap(
            risk_level, skill_out, advisor_out, mentor_out, time_to_job, sample
        )

        return {
            "skill_coach":        skill_out,
            "placement_advisor":  advisor_out,
            "interview_mentor":   mentor_out,
            "top_actions":        top_actions,
            "improvement_roadmap": roadmap,
        }


# ── LLM-Powered Dynamic Roadmap ───────────────────────────────────────────────

def _build_roadmap(
    risk_level: str,
    skill_out: Dict,
    advisor_out: Dict,
    mentor_out: Dict,
    time_to_job: float,
    sample: Dict[str, Any]
) -> List[Dict[str, str]]:
    """Calculates strict time horizons in Python and uses Groq to generate the text."""
    
    # 1. Gather all the data
    months_out = round(max(1.0, time_to_job), 1)
    total_months = math.ceil(months_out)

    # --- THE FIX: Python calculates the exact phases, not the LLM ---
    def format_phase(start, end):
        return f"Month {start}" if start == end else f"Month {start}-{end}"

    if total_months <= 1:
        phases = ["Week 1", "Week 2", "Week 3", "Week 4 (Final)"]
    elif total_months == 2:
        phases = ["Week 1-2", "Week 3-4", "Week 5-6", "Week 7-8 (Final)"]
    elif total_months == 3:
        phases = ["Week 1-3", "Week 4-6", "Week 7-9", "Week 10-12 (Final)"]
    else:
        p1 = int(total_months * 0.25)
        p2 = int(total_months * 0.50)
        p3 = int(total_months * 0.75)
        phases = [
            format_phase(1, max(1, p1)),
            format_phase(max(1, p1) + 1, max(p1 + 1, p2)),
            format_phase(max(p1 + 1, p2) + 1, max(p2 + 1, p3)),
            format_phase(max(p2 + 1, p3) + 1, total_months)
        ]

    profile_context = {
        "cgpa": sample.get("cgpa", 7.0),
        "internships": sample.get("internship_count", 0),
        "skills": sample.get("skill_list", ["Core Programming"]),
        "risk_level": risk_level,
        "target_tier": advisor_out.get("target_tier", "Tier-3"),
    }

    # 2. Craft the strictly constrained prompt
    system_prompt = f"""You are an expert Placement Officer at SPIT in Mumbai.
    Create a 4-step hyper-personalized placement roadmap for this student.

    You MUST output your response as valid JSON in this exact structure. 
    DO NOT alter the "phase" string values. I have already calculated the exact timeline for you:
    {{
      "roadmap": [
        {{"phase": "{phases[0]}", "focus": "Short title", "actions": "Detailed advice"}},
        {{"phase": "{phases[1]}", "focus": "Short title", "actions": "Detailed advice"}},
        {{"phase": "{phases[2]}", "focus": "Short title", "actions": "Detailed advice"}},
        {{"phase": "{phases[3]}", "focus": "Short title", "actions": "Detailed advice"}}
      ]
    }}
    """

    user_prompt = f"Create the roadmap for this student profile: {json.dumps(profile_context)}"

    # 3. Call the Free Groq API
    api_key = os.environ.get("GROQ_API_KEY", "YOUR_GROK_API_KEY") # Replace with your key
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant", 
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "response_format": {"type": "json_object"}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            llm_output = response.json()["choices"][0]["message"]["content"]
            roadmap_data = json.loads(llm_output)
            return roadmap_data.get("roadmap", [])
            
        else:
            print(f"API Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"LLM Call Failed: {e}")

    # 4. Fallback
    return [
        {
            "phase": "System Alert", 
            "focus": "Live Generation Paused", 
            "actions": "The LLM endpoint could not be reached. Please check your API key and internet connection."
        }
    ]