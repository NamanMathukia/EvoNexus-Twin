"""
src/agents/placement_advisor.py
Placement Advisor Agent — analyses internship signals and generates job strategy.
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Any


COMPANY_TIERS: Dict[str, Dict] = {
    "Tier-1": {
        "examples":      ["Google", "Microsoft", "Amazon", "Meta", "Goldman Sachs"],
        "cgpa_cutoff":   8.0,
        "skill_cutoff":  0.60,
        "intern_needed": True,
    },
    "Tier-2": {
        "examples":      ["TCS Digital", "Infosys SP", "Wipro Turbo", "Capgemini", "Deloitte"],
        "cgpa_cutoff":   7.0,
        "skill_cutoff":  0.35,
        "intern_needed": False,
    },
    "Tier-3": {
        "examples":      ["Startups", "SMEs", "Product companies", "Service firms"],
        "cgpa_cutoff":   5.5,
        "skill_cutoff":  0.20,
        "intern_needed": False,
    },
}

APPLICATION_PLATFORMS = [
    "LinkedIn (set profile to Open-to-Work)",
    "Naukri.com (premium listing recommended)",
    "Instahyre (AI-based matching)",
    "AngelList / Wellfound (startups)",
    "Company career portals directly",
]


class PlacementAdvisorAgent:
    """
    Analyses placement risk, internship quality, and market signals
    to produce a targeted job application strategy.
    """

    def run(
        self,
        shap_drivers: List[Tuple[str, float]],
        risk_level: str,
        cgpa: float,
        skill_score: float,
        n_internships: int,
        time_to_job: float,
        salary_estimate: float,
    ) -> Dict[str, Any]:
        """
        Returns
        -------
        dict with keys: target_tier, companies, application_strategy,
                        timeline_months, salary_negotiation_tips
        """
        # Determine realistic target tier
        target_tier = "Tier-3"
        for tier, criteria in COMPANY_TIERS.items():
            if (cgpa >= criteria["cgpa_cutoff"]
                    and skill_score >= criteria["skill_cutoff"]
                    and (not criteria["intern_needed"] or n_internships > 0)):
                target_tier = tier

        # Identify internship-related SHAP risks
        intern_risky = any(
            "intern" in f and v > 0 for f, v in shap_drivers
        )

        # Application cadence
        applications_per_week = {
            "High":   15,
            "Medium":  8,
            "Low":     4,
        }.get(risk_level, 8)

        strategy_points = [
            f"Target {target_tier} companies first: {', '.join(COMPANY_TIERS[target_tier]['examples'][:3])}",
            f"Apply to {applications_per_week} companies per week via {APPLICATION_PLATFORMS[0]}",
            "Customise CV for each role (ATS-optimised, keyword-matched)",
        ]
        if intern_risky and n_internships == 0:
            strategy_points.append(
                "URGENT: Secure a micro-internship or freelance project within 4 weeks to address gap"
            )
        if risk_level == "High":
            strategy_points.append(
                "Simultaneously target off-campus drives and walk-in interviews"
            )

        # Salary negotiation
        if salary_estimate < 5.0:
            nego_tip = "Focus on offer conversion; negotiate after 3 months of performance review."
        elif salary_estimate < 10.0:
            nego_tip = (
                f"Benchmark is ₹{salary_estimate:.1f}L. Counter-offer 10-15% above if skills justify."
            )
        else:
            nego_tip = (
                f"Strong profile (₹{salary_estimate:.1f}L expected). Negotiate ESOPs + signing bonus."
            )

        return {
            "target_tier":          target_tier,
            "target_companies":     COMPANY_TIERS[target_tier]["examples"],
            "application_strategy": strategy_points,
            "platforms":            APPLICATION_PLATFORMS[:3],
            "applications_per_week": applications_per_week,
            "estimated_months":     round(time_to_job, 1),
            "salary_negotiation":   nego_tip,
        }
