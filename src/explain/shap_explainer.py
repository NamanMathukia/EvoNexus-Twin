"""
src/explain/shap_explainer.py
SHAP-based explainability for the XGBoost risk model.
"""
from __future__ import annotations

from typing import List, Tuple, Optional

import numpy as np
import pandas as pd
import shap


class SHAPExplainer:
    """
    Lazy-initialised SHAP explainer around the risk XGBoost model.

    Parameters
    ----------
    risk_model : RiskModel instance (already loaded)
    """

    def __init__(self, risk_model) -> None:
        self._risk_model = risk_model
        self._explainer: Optional[shap.Explainer] = None

    def _get_explainer(self) -> shap.Explainer:
        if self._explainer is None:
            self._explainer = shap.Explainer(self._risk_model.model)
        return self._explainer

    def _high_risk_class_idx(self) -> int:
        classes = list(self._risk_model.encoder.classes_)
        return classes.index("High") if "High" in classes else 0

    def explain(
        self,
        X: pd.DataFrame,
        top_n: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Return top-N SHAP drivers as (feature_name, shap_value) sorted by |impact|.

        Parameters
        ----------
        X     : single-row preprocessed DataFrame
        top_n : number of top features to return
        """
        explainer  = self._get_explainer()
        shap_vals  = explainer(X)
        class_idx  = self._high_risk_class_idx()

        if len(shap_vals.values.shape) == 3:
            values = shap_vals.values[0, :, class_idx]
        else:
            values = shap_vals.values[0, :]

        features = list(X.columns)
        pairs    = list(zip(features, values.tolist()))
        return sorted(pairs, key=lambda x: abs(x[1]), reverse=True)[:top_n]

    def get_interactions(
        self,
        X: pd.DataFrame,
        top_n: int = 3,
    ) -> List[Tuple[str, float]]:
        """
        Approximate pairwise interaction scores from SHAP value products.

        Returns list of (feature_pair_label, interaction_score).
        """
        explainer  = self._get_explainer()
        shap_vals  = explainer(X)
        class_idx  = self._high_risk_class_idx()

        if len(shap_vals.values.shape) == 3:
            values = shap_vals.values[0, :, class_idx]
        else:
            values = shap_vals.values[0, :]

        features = list(X.columns)
        scores: List[Tuple[str, float]] = []
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                score = float(values[i] * values[j])
                scores.append((f"{features[i]} ✕ {features[j]}", score))

        return sorted(scores, key=lambda x: abs(x[1]), reverse=True)[:top_n]
