import shap
import numpy as np

def explain_prediction(df_sample, explainer, risk_encoder):
    shap_vals = explainer(df_sample)
    class_idx = list(risk_encoder.classes_).index("High")

    values = shap_vals.values[0, :, class_idx]
    features = df_sample.columns

    return sorted(zip(features, values), key=lambda x: abs(x[1]), reverse=True)[:3]


def get_top_interactions(df_sample, explainer, risk_encoder):
    shap_vals = explainer(df_sample)
    class_idx = list(risk_encoder.classes_).index("High")

    values = shap_vals.values[0, :, class_idx]
    features = df_sample.columns

    scores = []
    for i in range(len(features)):
        for j in range(i+1, len(features)):
            scores.append((f"{features[i]} + {features[j]}", float(values[i]*values[j])))

    return sorted(scores, key=lambda x: abs(x[1]), reverse=True)[:3]