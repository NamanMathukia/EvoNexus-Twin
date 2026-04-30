"""
src/data/generator.py
Synthetic student trajectory dataset generator.
Produces:
  - flat pandas DataFrame (for tabular models)
  - list of StudentProfile dicts (for graph / sequence models)
  - temporal triplets per student
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any

# ── Constants ─────────────────────────────────────────────────────────────────

SKILL_VOCABULARY: List[str] = [
    "python", "java", "javascript", "react", "nodejs",
    "sql", "machine_learning", "deep_learning", "data_analysis",
    "cloud_aws", "cloud_gcp", "docker", "kubernetes", "git",
    "communication", "leadership", "project_management",
    "statistics", "linear_algebra", "algorithms",
    "system_design", "api_design", "agile", "testing",
    "excel", "tableau", "power_bi", "r_programming",
    "nlp", "computer_vision",
]

SKILL_DEMAND: Dict[str, float] = {
    "python": 0.95, "machine_learning": 0.90, "deep_learning": 0.85,
    "cloud_aws": 0.88, "docker": 0.80, "kubernetes": 0.75,
    "react": 0.82, "nodejs": 0.78, "sql": 0.85, "data_analysis": 0.87,
    "java": 0.75, "javascript": 0.80, "system_design": 0.85,
    "git": 0.90, "communication": 0.70, "leadership": 0.65,
    "statistics": 0.78, "linear_algebra": 0.72, "algorithms": 0.82,
    "api_design": 0.75, "agile": 0.70, "testing": 0.72,
    "cloud_gcp": 0.80, "nlp": 0.83, "computer_vision": 0.82,
    "r_programming": 0.65, "tableau": 0.68, "power_bi": 0.65,
    "excel": 0.60, "project_management": 0.68,
}

COMPANIES: Dict[str, List[str]] = {
    "top":     ["Google", "Microsoft", "Amazon", "Meta", "Apple"],
    "mid":     ["TCS", "Infosys", "Wipro", "Accenture", "Cognizant"],
    "startup": ["Razorpay", "CRED", "Groww", "Slice", "Meesho"],
}

JOB_ROLES: List[str] = [
    "SDE-I", "Data Analyst", "ML Engineer", "Cloud Engineer",
    "QA Engineer", "Product Analyst", "Backend Engineer",
]

N_SEMESTERS: int = 8
SKILL_VOCAB_SIZE: int = len(SKILL_VOCABULARY)
SKILL_TO_IDX: Dict[str, int] = {s: i for i, s in enumerate(SKILL_VOCABULARY)}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _market_demand(semester: int, rng: np.random.Generator) -> float:
    base = 0.70 + 0.15 * np.sin(semester * np.pi / 4.0)
    return float(np.clip(base + rng.normal(0, 0.04), 0.2, 1.0))


def _compute_placement_score(
    final_cgpa: float,
    skill_score: float,
    n_internships: int,
    avg_quality: float,
    portal_activity: float,
    interviews: int,
) -> float:
    score = (
        0.25 * (final_cgpa / 10.0)
        + 0.30 * skill_score
        + 0.20 * min(n_internships / 2.0, 1.0)
        + 0.10 * avg_quality
        + 0.10 * portal_activity
        + 0.05 * min(interviews / 8.0, 1.0)
    )
    return float(np.clip(score, 0.0, 1.0))


# ── Main generator ────────────────────────────────────────────────────────────

def generate_student(student_idx: int, rng: np.random.Generator) -> Dict[str, Any]:
    """Generate one student's full trajectory and derived flat features."""
    student_id = f"S{student_idx:05d}"

    # ── Academic trajectory ────────────────────────────────────────────────
    academic_consistency = float(rng.beta(5, 2))
    base_cgpa = float(np.clip(rng.normal(7.2, 0.9), 4.0, 10.0))
    cgpas: List[float] = []
    cgpa = base_cgpa
    for _ in range(N_SEMESTERS):
        drift = rng.normal(0, 0.25) * (1.0 - academic_consistency)
        cgpa = float(np.clip(cgpa + drift, 4.0, 10.0))
        cgpas.append(round(cgpa, 2))
    final_cgpa = round(float(np.mean(cgpas[-2:])), 2)

    # ── Skill acquisition ─────────────────────────────────────────────────
    acquired: set = set()
    skill_timeline: List[Tuple[int, str]] = []

    n_base = int(rng.integers(1, 4))
    base_skills = rng.choice(SKILL_VOCABULARY, n_base, replace=False).tolist()
    for s in base_skills:
        acquired.add(s)
        skill_timeline.append((0, s))

    for sem in range(1, N_SEMESTERS):
        skill_prob = 0.25 + 0.10 * (sem / N_SEMESTERS)
        if rng.random() < skill_prob:
            n_new = int(rng.integers(1, 3))
            candidates = [s for s in SKILL_VOCABULARY if s not in acquired]
            if candidates:
                picks = rng.choice(candidates, min(n_new, len(candidates)), replace=False).tolist()
                for s in picks:
                    acquired.add(s)
                    skill_timeline.append((sem, s))

    final_skills = sorted(acquired)
    skill_score = round(len(final_skills) / SKILL_VOCAB_SIZE, 4)

    # ── Internships ───────────────────────────────────────────────────────
    internship_prob = 0.4 + 0.3 * (final_cgpa / 10.0) + 0.2 * skill_score
    internships: List[Dict[str, Any]] = []
    for _ in range(3):
        if rng.random() < internship_prob / 3.0:
            tier = str(rng.choice(["top", "mid", "startup"], p=[0.15, 0.55, 0.30]))
            company = str(rng.choice(COMPANIES[tier]))
            role = str(rng.choice(JOB_ROLES))
            duration = int(rng.integers(2, 7))
            semester = int(rng.integers(4, N_SEMESTERS))
            quality_base = {"top": 0.90, "mid": 0.60, "startup": 0.75}[tier]
            quality = float(np.clip(quality_base + rng.normal(0, 0.05), 0.1, 1.0))
            internships.append({
                "company": company, "role": role, "duration": duration,
                "semester": semester, "quality": quality, "tier": tier,
            })

    n_internships = len(internships)
    avg_quality = float(np.mean([i["quality"] for i in internships])) if internships else 0.0

    # ── Engagement signals ────────────────────────────────────────────────
    portal_activity = float(np.clip(rng.beta(3, 2) * (0.5 + 0.5 * skill_score), 0.0, 1.0))
    resume_updates = int(rng.integers(0, 8))
    interviews = int(rng.integers(0, 10))

    # ── Placement outcome ─────────────────────────────────────────────────
    placement_score = _compute_placement_score(
        final_cgpa, skill_score, n_internships, avg_quality, portal_activity, interviews
    )
    placement_score = float(np.clip(placement_score + rng.normal(0, 0.04), 0.0, 1.0))

    if placement_score >= 0.65:
        risk_level = "Low"
    elif placement_score >= 0.45:
        risk_level = "Medium"
    else:
        risk_level = "High"

    placed = bool(rng.random() < placement_score)
    months_to_placement = float(
        np.clip(rng.normal(max(1.0, 12.0 - placement_score * 10.0), 1.5), 1.0, 18.0)
        if placed else 24.0
    )

    # ── Salary ────────────────────────────────────────────────────────────
    if placed:
        base_sal = 4.0 + 12.0 * placement_score
        if internships:
            best_tier = max(internships, key=lambda x: x["quality"])["tier"]
            base_sal += {"top": 8.0, "mid": 2.0, "startup": 4.0}[best_tier] * 0.3
        salary = float(np.clip(rng.normal(base_sal, 1.5), 3.0, 50.0))
    else:
        salary = 0.0

    # ── Trajectory steps ──────────────────────────────────────────────────
    trajectory: List[Dict[str, Any]] = []
    cum: set = set()
    for sem in range(N_SEMESTERS):
        sem_skills = [s for (t, s) in skill_timeline if t == sem]
        cum.update(sem_skills)
        has_intern = any(i["semester"] == sem for i in internships)
        intern_co = next((i["company"] for i in internships if i["semester"] == sem), None)
        trajectory.append({
            "semester": sem,
            "cgpa": cgpas[sem],
            "skills_this_sem": sem_skills,
            "cum_skill_count": len(cum),
            "has_internship": has_intern,
            "internship_company": intern_co,
            "market_demand": _market_demand(sem, rng),
            "engagement_score": float(portal_activity * (0.8 + 0.2 * (sem / N_SEMESTERS))),
            "portal_activity": portal_activity,
        })

    # ── Temporal triplets ─────────────────────────────────────────────────
    triplets: List[Dict[str, Any]] = []
    for (sem, skill) in skill_timeline:
        triplets.append({"event_type": "skill_acquired", "entity": skill,
                         "timestamp": float(sem * 6.0)})
    for intern in internships:
        triplets.append({"event_type": "internship", "entity": intern["company"],
                         "timestamp": float(intern["semester"] * 6.0)})
    if placed:
        triplets.append({"event_type": "placed", "entity": "placement",
                         "timestamp": 48.0 - months_to_placement})

    # ── Flat feature row ──────────────────────────────────────────────────
    flat: Dict[str, Any] = {
        "student_id": student_id,
        "cgpa": final_cgpa,
        "academic_consistency": round(academic_consistency, 4),
        "skills": skill_score,
        "internship": min(n_internships, 1),        # binary flag
        "internship_count": n_internships,
        "internship_quality": round(avg_quality, 4),
        "portal_activity": round(portal_activity, 4),
        "resume_updates": resume_updates,
        "interviews": interviews,
        "skill_demand_score": round(
            float(np.mean([SKILL_DEMAND.get(s, 0.5) for s in final_skills])) if final_skills else 0.5, 4
        ),
        "placed": int(placed),
        "months_to_placement": round(months_to_placement, 2),
        "risk_level": risk_level,
        "actual_salary": round(salary, 2),
        "placement_score": round(placement_score, 4),
    }

    return {
        "student_id": student_id,
        "flat": flat,
        "trajectory": trajectory,
        "triplets": triplets,
        "internships": internships,
        "final_skills": final_skills,
        "final_cgpa": final_cgpa,
        "skill_score": skill_score,
        "n_internships": n_internships,
        "avg_internship_quality": avg_quality,
        "portal_activity": portal_activity,
        "resume_updates": resume_updates,
        "interviews": interviews,
        "placed": placed,
        "months_to_placement": months_to_placement,
        "salary": salary,
        "risk_level": risk_level,
        "placement_score": placement_score,
    }


def generate_dataset(
    n_students: int = 6000,
    seed: int = 42,
) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Generate full synthetic dataset.

    Returns
    -------
    df : pd.DataFrame
        Flat tabular representation (one row per student).
    profiles : list[dict]
        Rich trajectory/triplet representation (one dict per student).
    """
    rng = np.random.default_rng(seed)
    profiles: List[Dict[str, Any]] = []
    flat_rows: List[Dict[str, Any]] = []

    for idx in range(n_students):
        student = generate_student(idx, rng)
        profiles.append(student)
        flat_rows.append(student["flat"])

    df = pd.DataFrame(flat_rows)
    return df, profiles


def build_trajectory_sequences(profiles: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert profiles to LSTM-ready numpy arrays.

    Returns
    -------
    X : ndarray of shape (N, N_SEMESTERS, 6)
        [cgpa_norm, cum_skills_norm, has_intern, market_demand, engagement, portal_activity]
    y : ndarray of shape (N,)
        Placement outcome (0/1)
    """
    X_list, y_list = [], []
    for student in profiles:
        seq = []
        for step in student["trajectory"]:
            seq.append([
                step["cgpa"] / 10.0,
                step["cum_skill_count"] / SKILL_VOCAB_SIZE,
                float(step["has_internship"]),
                step["market_demand"],
                step["engagement_score"],
                step["portal_activity"],
            ])
        X_list.append(seq)
        y_list.append(float(student["placed"]))
    return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.float32)


def build_skill_sets(profiles: List[Dict[str, Any]]) -> Tuple[List[List[int]], np.ndarray]:
    """
    Convert profiles to SetNet-ready skill index lists.

    Returns
    -------
    skill_sets : list of list[int]  (variable length)
    y          : ndarray of shape (N,)
    """
    skill_sets = []
    y_list = []
    for student in profiles:
        indices = [SKILL_TO_IDX[s] for s in student["final_skills"] if s in SKILL_TO_IDX]
        skill_sets.append(indices if indices else [0])
        y_list.append(float(student["placed"]))
    return skill_sets, np.array(y_list, dtype=np.float32)


if __name__ == "__main__":
    print("Generating 6000 students …")
    df, profiles = generate_dataset(6000)
    print(f"DataFrame shape: {df.shape}")
    print(df["risk_level"].value_counts())
    print(df.head(3))
