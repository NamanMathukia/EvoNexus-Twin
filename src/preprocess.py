"""
src/preprocess.py
Preprocessing utilities for both training-time and inference-time pipelines.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from src.features import (
    add_trajectory_features,
    get_feature_columns,
    ALL_MODEL_FEATURES,
    GRAPH_FEATURES,
    NEURAL_FEATURES,
)


def preprocess_dataframe(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Apply feature engineering and return clean model-input DataFrame.
    Handles missing columns gracefully by filling with zeros.
    """
    df = add_trajectory_features(df)

    if feature_cols is None:
        feature_cols = get_feature_columns(df)

    # Fill missing graph/neural columns with neutral defaults
    for col in GRAPH_FEATURES:
        if col not in df.columns:
            df[col] = 0.0
    for col in NEURAL_FEATURES:
        if col not in df.columns:
            df[col] = 0.5

    df = df.reindex(columns=feature_cols, fill_value=0.0)
    df = df.replace([np.inf, -np.inf], 0.0)
    df = df.fillna(0.0)
    return df


def preprocess_sample(
    sample_dict: Dict,
    feature_cols: List[str],
) -> pd.DataFrame:
    """
    Convert a single raw student dict to a model-ready single-row DataFrame.

    Parameters
    ----------
    sample_dict  : raw input (may contain extra or missing keys)
    feature_cols : list of column names the model expects
    """
    df = pd.DataFrame([sample_dict])

    # Ensure base numeric columns exist with defaults
    defaults = {
        "cgpa": 7.0, "skills": 0.3, "internship": 0,
        "academic_consistency": 0.7, "internship_quality": 0.0,
        "portal_activity": 0.5, "resume_updates": 2,
        "interviews": 3, "skill_demand_score": 0.7,
        "lstm_prob": 0.5, "set_net_prob": 0.5,
        **{g: 0.0 for g in GRAPH_FEATURES},
    }
    for k, v in defaults.items():
        if k not in df.columns:
            df[k] = v

    return preprocess_dataframe(df, feature_cols=feature_cols)