"""
main.py  — CLI demo entrypoint.
Run: python main.py
"""
import json
from src.predict import predict_full

SAMPLE_STUDENT = {
    "cgpa":                 7.8,
    "skills":               0.55,
    "internship":           1,
    "internship_count":     2,
    "internship_quality":   0.72,
    "academic_consistency": 0.80,
    "portal_activity":      0.65,
    "resume_updates":       3,
    "interviews":           5,
    "skill_demand_score":   0.78,
    "skill_list":           ["python", "sql", "machine_learning", "docker", "git"],
    "market_demand":        0.75,
}

if __name__ == "__main__":
    print("\n🎯 EvoNexus-Twin — Full Inference Demo\n")
    result = predict_full(SAMPLE_STUDENT)

    print("=" * 60)
    print(f"  Risk Level    : {result['risk']}")
    print(f"  Salary (LPA)  : ₹{result['salary']:.2f}")
    print(f"  Time to Job   : {result['time_to_job']:.1f} months")
    print(f"  LSTM P(place) : {result['lstm_prob']:.3f}")
    print(f"  SetNet P(pl.) : {result['set_net_prob']:.3f}")
    print("=" * 60)

    print("\n📊 Top SHAP Drivers:")
    for feat, val in result["drivers"]:
        arrow = "▲" if val > 0 else "▼"
        print(f"  {arrow} {feat:35s} {val:+.4f}")

    print("\n🔗 Top Feature Interactions:")
    for pair, val in result["interactions"]:
        print(f"  {pair:50s} {val:+.6f}")

    print("\n🤖 NBA Action Plan:")
    for action in result["actions"]["top_actions"]:
        print(f"  • {action}")

    print("\n🗺  Improvement Roadmap:")
    for milestone in result["actions"]["improvement_roadmap"]:
        print(f"  [{milestone['phase']}] {milestone['focus']}: {milestone['actions']}")

    print("\n📝 Executive Summary:")
    print(f"  {result['summary']}")
    print()