"""
src/features.py
Feature engineering shared across training and inference pipelines.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ── Tabular trajectory-derived features ──────────────────────────────────────

def add_trajectory_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived features from base columns (in-place safe copy)."""
    df = df.copy()
    df["cgpa_trend"]           = df["cgpa"] * df["academic_consistency"]
    df["skill_velocity"]       = df["skills"] * df["portal_activity"]
    df["internship_intensity"] = df["internship"] * df["internship_quality"]
    df["engagement_score"]     = (
        df["portal_activity"]
        + df["resume_updates"].clip(upper=7) / 7.0
        + df["interviews"].clip(upper=9) / 9.0
    ) / 3.0
    df["skill_demand_weighted"] = (
        df["skills"] * df.get("skill_demand_score", 0.7)
    )
    df["composite_readiness"]  = (
        0.25 * (df["cgpa"] / 10.0)
        + 0.25 * df["skills"]
        + 0.20 * df["internship_intensity"]
        + 0.15 * df["engagement_score"]
        + 0.15 * df.get("skill_demand_score", pd.Series(0.7, index=df.index))
    )
    return df


# ── Model column sets ─────────────────────────────────────────────────────────

CORE_FEATURES = [
    "cgpa", "skills", "internship", "academic_consistency",
    "internship_quality", "portal_activity", "resume_updates",
    "interviews", "skill_demand_score",
]

DERIVED_FEATURES = [
    "cgpa_trend", "skill_velocity", "internship_intensity",
    "engagement_score", "skill_demand_weighted", "composite_readiness",
]

GRAPH_FEATURES = [
    "graph_degree", "graph_out_degree", "graph_centrality",
    "graph_betweenness", "graph_skill_degree", "graph_job_degree",
    "graph_avg_skill_rarity",
]

NEURAL_FEATURES = ["lstm_prob", "set_net_prob"]

ALL_MODEL_FEATURES = CORE_FEATURES + DERIVED_FEATURES + GRAPH_FEATURES + NEURAL_FEATURES

TARGET_RISK   = "risk_level"
TARGET_SALARY = "actual_salary"
DURATION_COL  = "months_to_placement"
EVENT_COL     = "placed"
DROP_COLS     = ["student_id", TARGET_RISK, TARGET_SALARY, DURATION_COL, EVENT_COL,
                 "placement_score", "internship_count"]


def get_feature_columns(df: pd.DataFrame) -> list:
    """Return model feature columns available in df (filters to intersection)."""
    return [c for c in ALL_MODEL_FEATURES if c in df.columns]