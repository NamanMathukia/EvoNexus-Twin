"""
src/models/salary.py
LightGBM salary regressor wrapper.
"""
from __future__ import annotations

import os
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor

MODEL_PATH = os.path.join("models", "salary_model.pkl")


class SalaryModel:
    """Wraps LGBMRegressor for salary prediction."""

    def __init__(self) -> None:
        self.model = LGBMRegressor(
            n_estimators=400,
            learning_rate=0.05,
            max_depth=8,
            num_leaves=63,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1,
        )
        self.feature_names_: Optional[List[str]] = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "SalaryModel":
        self.feature_names_ = X.columns.tolist()
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        raw = self.model.predict(X)
        return np.clip(raw, 0.0, None)

    def predict_single(self, X: pd.DataFrame) -> float:
        return float(self.predict(X)[0])

    def save(self, path: str = MODEL_PATH) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        print(f"  [Salary] Saved -> {path}")

    @classmethod
    def load(cls, path: str = MODEL_PATH) -> "SalaryModel":
        inst = cls.__new__(cls)
        inst.model = joblib.load(path)
        inst.feature_names_ = None
        return inst
