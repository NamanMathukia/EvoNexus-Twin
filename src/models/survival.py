"""
src/models/survival.py
Lifelines WeibullAFTFitter wrapper for time-to-placement prediction.
"""
from __future__ import annotations

import os
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from lifelines import WeibullAFTFitter

MODEL_PATH = os.path.join("models", "survival_model.pkl")

# Features used for survival model (subset that lifelines handles well)
SURVIVAL_FEATURES = [
    "cgpa", "skills", "internship", "academic_consistency",
    "internship_quality", "portal_activity", "resume_updates",
    "interviews", "skill_demand_score",
    "lstm_prob", "set_net_prob",
    "graph_skill_degree", "graph_avg_skill_rarity",
]


class SurvivalModel:
    """Wraps WeibullAFTFitter with convenience fit/predict API."""

    def __init__(self) -> None:
        self.fitter = WeibullAFTFitter(penalizer=0.01)
        self._used_cols: Optional[list] = None

    def fit(self, df: pd.DataFrame) -> "SurvivalModel":
        """
        df must contain:
          - 'months_to_placement'  (duration column)
          - 'placed'               (event column, 1=placed, 0=censored)
          - feature columns
        """
        available = [c for c in SURVIVAL_FEATURES if c in df.columns]
        self._used_cols = available
        fit_df = df[available + ["months_to_placement", "placed"]].copy()
        fit_df = fit_df.replace([np.inf, -np.inf], np.nan).dropna()
        self.fitter.fit(fit_df, duration_col="months_to_placement", event_col="placed")
        return self

    def predict_expectation(self, X: pd.DataFrame) -> np.ndarray:
        available = [c for c in (self._used_cols or SURVIVAL_FEATURES) if c in X.columns]
        X_sub = X[available].copy()
        result = self.fitter.predict_expectation(X_sub)
        return np.clip(result.values, 1.0, 36.0)

    def predict_single(self, X: pd.DataFrame) -> float:
        return float(self.predict_expectation(X)[0])

    def save(self, path: str = MODEL_PATH) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        print(f"  [Survival] Saved -> {path}")

    @classmethod
    def load(cls, path: str = MODEL_PATH) -> "SurvivalModel":
        return joblib.load(path)
