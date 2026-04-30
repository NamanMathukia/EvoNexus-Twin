"""
src/agents/skill_coach.py
Skill Coach Agent — analyses skill gaps and generates learning roadmap.
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Any

# High-demand skill clusters
SKILL_CLUSTERS: Dict[str, List[str]] = {
    "Data Science":  ["python", "machine_learning", "deep_learning", "statistics", "sql"],
    "Cloud & DevOps": ["cloud_aws", "docker", "kubernetes", "cloud_gcp", "git"],
    "Full Stack":    ["javascript", "react", "nodejs", "api_design", "sql"],
    "Analytics":     ["tableau", "power_bi", "excel", "data_analysis", "r_programming"],
    "Core CS":       ["algorithms", "system_design", "testing", "agile", "git"],
}

CERTIFICATIONS: Dict[str, str] = {
    "python":           "Python for Everybody — Coursera",
    "machine_learning": "Andrew Ng ML Specialisation — Coursera",
    "deep_learning":    "Deep Learning Specialisation — Coursera",
    "cloud_aws":        "AWS Solutions Architect Associate",
    "docker":           "Docker & Kubernetes — Udemy",
    "react":            "React — The Complete Guide (Udemy)",
    "sql":              "SQL for Data Science — Coursera",
    "statistics":       "Statistics with Python — Coursera",
    "system_design":    "Grokking System Design — Educative",
    "algorithms":       "Algorithms Specialisation — Stanford/Coursera",
    "data_analysis":    "Google Data Analytics Certificate",
    "tableau":          "Tableau Desktop Specialist",
    "nlp":              "NLP Specialisation — Coursera",
    "computer_vision":  "Deep Learning for CV — Fast.ai",
}


class SkillCoachAgent:
    """
    Analyses SHAP drivers to identify skill-related gaps
    and produces a structured improvement roadmap.
    """

    def run(
        self,
        shap_drivers: List[Tuple[str, float]],
        skill_score: float,
        current_skills: List[str],
        risk_level: str,
    ) -> Dict[str, Any]:
        """
        Parameters
        ----------
        shap_drivers   : [(feature_name, shap_value), ...]
        skill_score    : 0-1 normalised skill breadth
        current_skills : list of skill names the student already has
        risk_level     : "High" | "Medium" | "Low"

        Returns
        -------
        dict with keys: gap_analysis, priority_skills, certifications, timeline_weeks
        """
        # Identify skill-related SHAP drivers with positive impact on risk
        risky_skill_features = [
            f for f, v in shap_drivers
            if ("skill" in f or "lstm" in f or "set_net" in f) and v > 0
        ]

        # Determine missing high-demand skills
        current_set = set(current_skills)
        all_high_demand = {
            s for cluster in SKILL_CLUSTERS.values() for s in cluster
        }
        missing = sorted(all_high_demand - current_set)

        # Prioritise: skills that appear in high-demand clusters AND are missing
        priority = []
        for cluster_name, cluster_skills in SKILL_CLUSTERS.items():
            gap = [s for s in cluster_skills if s not in current_set]
            if gap:
                priority.append({"cluster": cluster_name, "missing_skills": gap[:3]})

        # Recommend certifications for top-3 missing skills
        top_missing = missing[:5]
        cert_recs   = [
            {"skill": s, "certification": CERTIFICATIONS.get(s, f"Search Udemy/Coursera for {s}")}
            for s in top_missing
        ]

        # Timeline estimate
        n_missing = len(missing)
        if risk_level == "High":
            timeline = max(8, n_missing * 2)
        elif risk_level == "Medium":
            timeline = max(4, n_missing * 1)
        else:
            timeline = max(2, n_missing // 2)

        gap_summary = (
            f"You currently have {len(current_set)} of {len(all_high_demand)} high-demand skills. "
            f"{len(missing)} skills gap{'s' if len(missing) != 1 else ''} identified."
        )
        if risky_skill_features:
            gap_summary += f" SHAP signals '{risky_skill_features[0]}' as your primary skill risk driver."

        return {
            "gap_analysis":   gap_summary,
            "priority_skills": priority[:3],
            "certifications": cert_recs,
            "timeline_weeks": timeline,
            "action_items": [
                f"Complete {cert_recs[0]['certification']}" if cert_recs else "Broaden skill portfolio",
                "Build 2 GitHub projects showcasing top skills",
                "Contribute to an open-source project in target domain",
            ],
        }
