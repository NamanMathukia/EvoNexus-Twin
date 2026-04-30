def agentic_recommendation(top_features, risk):
    actions = []

    for f, val in top_features:
        if "skills" in f and val > 0:
            actions.append("Take advanced certification")
        if "internship" in f and val > 0:
            actions.append("Apply to internships immediately")
        if "cgpa" in f and val > 0:
            actions.append("Improve academics")

    if risk == "High":
        actions.append("Weekly mock interviews + resume review")

    if not actions:
        actions.append("Maintain current performance and target top recruiters")

    return list(set(actions))


def generate_executive_output(result):

    def interpret(feature, impact):
        name_map = {
            "cgpa": "academic performance",
            "internship": "internship experience",
            "internship_quality": "quality of internship exposure",
            "interviews": "interview performance",
            "skills": "technical skill level"
        }

        name = name_map.get(feature, feature.replace("_", " "))

        if impact > 0:
            return f"{name} is contributing to higher placement risk"
        else:
            return f"{name} is helping reduce placement risk"

    drivers = [interpret(f, v) for f, v in result["Drivers"]]

    interactions = [
        f"{pair} shows strong {'positive synergy' if val > 0 else 'negative dependency'}"
        for pair, val in result["Interactions"]
    ]

    actions = list(set(result["Actions"]))

    return f"""
This candidate has a {result['Risk']} placement risk profile with an expected starting salary of {result['Salary']} LPA.
They are projected to secure employment within approximately {result['Time_to_job']} months.

The primary drivers influencing this outcome are:
- {drivers[0]}
- {drivers[1]}
- {drivers[2]}

Additionally, key skill interactions indicate:
- {interactions[0]}
- {interactions[1]}

Recommended intervention:
- {"; ".join(actions)}
"""