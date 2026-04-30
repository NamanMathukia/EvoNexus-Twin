import pandas as pd
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from lightgbm import LGBMRegressor
from lifelines import WeibullAFTFitter

from src.features import add_trajectory_features

# Load data
df = pd.read_csv("data/final_balanced_dataset.csv")
df = add_trajectory_features(df)

drop_cols = [
    "risk_explanation","recommended_action",
    "placement_3m_prob","placement_6m_prob","placement_12m_prob"
]

df_model = df.drop(columns=drop_cols)

y_risk = df_model["risk_level"]
y_salary = df_model["actual_salary"]

df_model = df_model.drop(columns=["risk_level","actual_salary"])

# Encode
feature_encoders = {}
for col in df_model.select_dtypes(include='object').columns:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col])
    feature_encoders[col] = le

risk_encoder = LabelEncoder()
y_risk_encoded = risk_encoder.fit_transform(y_risk)

# Split
X_train, X_test, y_risk_train, _ = train_test_split(
    df_model, y_risk_encoded, test_size=0.2, random_state=42
)

_, _, y_salary_train, _ = train_test_split(
    df_model, y_salary, test_size=0.2, random_state=42
)

# Models
risk_model = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.05)
risk_model.fit(X_train, y_risk_train)

salary_model = LGBMRegressor(n_estimators=300)
salary_model.fit(X_train, y_salary_train)

# Survival
df_model["months_to_job"] = (12 - (df_model["skills"]*5 + df_model["cgpa"]*0.5)).clip(1,12)
df_model["is_placed"] = (df_model["months_to_job"] < 12).astype(int)

aft = WeibullAFTFitter()
aft.fit(df_model, duration_col="months_to_job", event_col="is_placed")

# Save models
joblib.dump(risk_model, "models/risk_model.pkl")
joblib.dump(salary_model, "models/salary_model.pkl")
joblib.dump(aft, "models/survival_model.pkl")
joblib.dump(feature_encoders, "models/encoders.pkl")
joblib.dump(risk_encoder, "models/risk_encoder.pkl")
joblib.dump(X_train.columns.tolist(), "models/features.pkl")

print("✅ Models saved successfully")