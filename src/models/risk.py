"""
src/models/risk.py
XGBoost risk classifier wrapper.
"""
from __future__ import annotations

import os
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

MODEL_PATH   = os.path.join("models", "risk_model.pkl")
ENCODER_PATH = os.path.join("models", "risk_encoder.pkl")


class RiskModel:
    """Wraps XGBClassifier with encode/decode of risk labels."""

    def __init__(self) -> None:
        self.model   = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="mlogloss",
            random_state=42,
        )
        self.encoder = LabelEncoder()
        self.feature_names_: Optional[List[str]] = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "RiskModel":
        self.feature_names_ = X.columns.tolist()
        y_enc = self.encoder.fit_transform(y)
        self.model.fit(X, y_enc)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.encoder.inverse_transform(self.model.predict(X))

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(X)

    def predict_single(self, X: pd.DataFrame) -> str:
        return str(self.predict(X)[0])

    def save(self, model_path: str = MODEL_PATH, encoder_path: str = ENCODER_PATH) -> None:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.model,   model_path)
        joblib.dump(self.encoder, encoder_path)
        print(f"  [Risk] Saved -> {model_path}")

    @classmethod
    def load(cls, model_path: str = MODEL_PATH, encoder_path: str = ENCODER_PATH) -> "RiskModel":
        inst = cls.__new__(cls)
        inst.model   = joblib.load(model_path)
        inst.encoder = joblib.load(encoder_path)
        inst.feature_names_ = None
        return inst
