"""
src/models/trainer.py
Unified training pipeline for all ENT models.

Steps
-----
1. Generate synthetic student data (6000 students)
2. Build Temporal Knowledge Graph → augment DataFrame with graph features
3. Train LSTM trajectory model   → augment DataFrame with lstm_prob
4. Train SetNet skill model      → augment DataFrame with set_net_prob
5. Feature-engineer augmented DataFrame
6. Train XGBoost risk classifier
7. Train LightGBM salary regressor
8. Train WeibullAFT survival model
9. Save all artifacts to models/
"""
from __future__ import annotations

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.data.generator import (
    generate_dataset,
    build_trajectory_sequences,
    build_skill_sets,
    SKILL_TO_IDX,
)
from src.graph.tkg import TemporalKnowledgeGraph
from src.models.trajectory import (
    train_trajectory_model,
    save_trajectory_model,
    predict_trajectory,
    synthesize_sequence_from_flat,
)
from src.models.set_net import (
    train_set_net,
    save_set_net,
    predict_set_placement,
)
from src.models.risk import RiskModel
from src.models.salary import SalaryModel
from src.models.survival import SurvivalModel
from src.features import (
    add_trajectory_features,
    get_feature_columns,
    DROP_COLS,
    ALL_MODEL_FEATURES,
)

MODELS_DIR = "models"


def _augment_with_neural(
    df: pd.DataFrame,
    profiles,
    lstm_model,
    set_net_model,
) -> pd.DataFrame:
    """Add lstm_prob and set_net_prob columns to df."""
    print("  Generating LSTM probabilities …")
    lstm_probs = []
    for student in profiles:
        seq = np.array([[
            step["cgpa"] / 10.0,
            step["cum_skill_count"] / 30.0,
            float(step["has_internship"]),
            step["market_demand"],
            step["engagement_score"],
            step["portal_activity"],
        ] for step in student["trajectory"]], dtype=np.float32)
        lstm_probs.append(predict_trajectory(lstm_model, seq))
    df["lstm_prob"] = lstm_probs

    print("  Generating SetNet probabilities …")
    sn_probs = []
    for student in profiles:
        indices = [SKILL_TO_IDX[s] for s in student["final_skills"] if s in SKILL_TO_IDX]
        if not indices:
            indices = [0]
        sn_probs.append(predict_set_placement(set_net_model, indices))
    df["set_net_prob"] = sn_probs

    return df


def train_all(n_students: int = 6000, seed: int = 42) -> None:
    os.makedirs(MODELS_DIR, exist_ok=True)

    # ── Step 1: Generate data ─────────────────────────────────────────────────
    print("\n[1/8] Generating synthetic dataset …")
    df, profiles = generate_dataset(n_students=n_students, seed=seed)
    print(f"      Dataset shape: {df.shape}")
    print(f"      Risk distribution:\n{df['risk_level'].value_counts().to_string()}")

    # ── Step 2: Build TKG ─────────────────────────────────────────────────────
    print("\n[2/8] Building Temporal Knowledge Graph …")
    tkg = TemporalKnowledgeGraph(profiles)
    summary = tkg.summary()
    print(f"      Nodes={summary['n_nodes']}  Edges={summary['n_edges']}")
    df = tkg.augment_dataframe(df)
    joblib.dump(tkg, os.path.join(MODELS_DIR, "tkg.pkl"))
    print("      TKG saved.")

    # ── Step 3: Train LSTM ────────────────────────────────────────────────────
    print("\n[3/8] Training LSTM trajectory model …")
    X_seq, y_seq = build_trajectory_sequences(profiles)
    lstm_model = train_trajectory_model(X_seq, y_seq, epochs=30)
    save_trajectory_model(lstm_model)

    # ── Step 4: Train SetNet ──────────────────────────────────────────────────
    print("\n[4/8] Training LGDESetNet …")
    skill_sets, y_sets = build_skill_sets(profiles)
    set_net_model = train_set_net(skill_sets, y_sets, epochs=30)
    save_set_net(set_net_model)

    # ── Step 5: Augment df with neural features ───────────────────────────────
    print("\n[5/8] Augmenting DataFrame with neural model outputs …")
    df = _augment_with_neural(df, profiles, lstm_model, set_net_model)

    # ── Step 6: Feature engineering ───────────────────────────────────────────
    print("\n[6/8] Feature engineering …")
    df = add_trajectory_features(df)
    feature_cols = [c for c in ALL_MODEL_FEATURES if c in df.columns]
    print(f"      Using {len(feature_cols)} features: {feature_cols}")

    # Persist feature list for inference
    joblib.dump(feature_cols, os.path.join(MODELS_DIR, "feature_cols.pkl"))

    X = df[feature_cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    y_risk   = df["risk_level"]
    y_salary = df["actual_salary"]

    X_train, X_test, yr_train, yr_test, ys_train, ys_test = train_test_split(
        X, y_risk, y_salary, test_size=0.15, random_state=seed
    )

    # ── Step 7: Train XGBoost risk model ─────────────────────────────────────
    print("\n[7/8] Training XGBoost risk classifier …")
    risk_model = RiskModel()
    risk_model.fit(X_train, yr_train)
    risk_model.save()

    # Quick eval
    preds = risk_model.predict(X_test)
    acc   = (preds == yr_test.values).mean()
    print(f"      Test accuracy: {acc:.3f}")

    # ── Step 8: Train LightGBM salary model (placed students only) ───────────
    print("\n[8/8a] Training LightGBM salary model (placed students only) ...")
    placed_mask = df["placed"] == 1
    n_placed    = placed_mask.sum()
    print(f"      Placed students for salary training: {n_placed}")

    X_placed  = X[placed_mask].reset_index(drop=True)
    y_placed  = df.loc[placed_mask, "actual_salary"].reset_index(drop=True)

    X_sal_train, X_sal_test, ys_sal_train, ys_sal_test = train_test_split(
        X_placed, y_placed, test_size=0.15, random_state=seed
    )

    salary_model = SalaryModel()
    salary_model.fit(X_sal_train, ys_sal_train)
    salary_model.save()

    sal_preds = salary_model.predict(X_sal_test)
    mae = np.mean(np.abs(sal_preds - ys_sal_test.values))
    print(f"      Salary MAE (placed only): {mae:.3f} LPA")
    print(f"      Range: {y_placed.min():.1f} - {y_placed.max():.1f} LPA  mean={y_placed.mean():.1f}")


    # ── Step 9: Train WeibullAFT survival model ───────────────────────────────
    print("\n[8/8b] Training WeibullAFT survival model …")
    survival_df = df.copy()
    survival_model = SurvivalModel()
    survival_model.fit(survival_df)
    survival_model.save()

    print("\nAll models trained and saved to models/ [DONE]")


if __name__ == "__main__":
    os.environ["PYTHONUTF8"] = "1"
    train_all()
