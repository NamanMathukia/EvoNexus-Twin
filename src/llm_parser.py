"""
src/llm_parser.py
Uses Groq (Llama 3.1) to parse resumes and generate dynamic agentic roadmaps.
"""
import os
import json
from groq import Groq
from datetime import date
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def parse_resume_to_features(resume_text: str) -> dict:
    """Parses resume text into strict feature JSON."""
    system_prompt = """
    You are an expert technical recruiter AI. Extract candidate metrics into strict JSON.
    Follow this schema exactly. Pay special attention to extracting the expected or actual graduation year:
    {
      "course": "Engineering", 
      "graduation_year": 2025,      // int (the 4-digit expected or actual graduation year)
      "cgpa": 7.5, "skills": 0.6,
      "skill_list": ["Python", "SQL"], "internship": 1, "internship_quality": 0.8,
      "academic_consistency": 0.7, "portal_activity": 0.5, "resume_updates": 2,
      "interviews": 3, "skill_demand_score": 0.8, "market_demand": 0.7
    }
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Parse this resume:\n\n{resume_text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        # 1. Load the raw LLM output
        raw_data = json.loads(response.choices[0].message.content)
        
        # 2. Ironclad Data Sanitizer
        numeric_fields = [
            "cgpa", "skills", "internship", "internship_quality", 
            "academic_consistency", "portal_activity", "resume_updates", 
            "interviews", "skill_demand_score", "market_demand", "graduation_year"
        ]
        
        for field in numeric_fields:
            if field in raw_data:
                val = raw_data[field]
                if isinstance(val, dict):
                    try:
                        raw_data[field] = float(list(val.values())[0])
                    except:
                        raw_data[field] = 0.0
                elif isinstance(val, list):
                    try:
                        raw_data[field] = float(val[0])
                    except:
                        raw_data[field] = 0.0
                else:
                    try:
                        raw_data[field] = float(val)
                    except (ValueError, TypeError):
                        pass 
                        
        if isinstance(raw_data.get("course"), dict):
            try:
                raw_data["course"] = str(list(raw_data["course"].values())[0])
            except:
                raw_data["course"] = "Engineering"
                
        return raw_data
        
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return {
            "course": "Engineering", "graduation_year": date.today().year + 1,
            "cgpa": 7.0, "skills": 0.3, "skill_list": ["Python"],
            "internship": 0, "internship_quality": 0.0, "academic_consistency": 0.7,
            "portal_activity": 0.5, "resume_updates": 1, "interviews": 1,
            "skill_demand_score": 0.5, "market_demand": 0.5
        }

def generate_dynamic_roadmap(time_to_job: float, skill_list: list, target_tier: str) -> list:
    """Generates a roadmap where the number of phases matches the time available."""
    
    # Handle past-due or immediate timelines
    if time_to_job <= 0.25:
        unit = "Day"
        value = 7
        num_phases = 3
        timeline_str = "7 Days (Immediate Action Required)"
    # Handle short timelines
    elif time_to_job < 1:
        unit = "Week"
        value = max(1, int(time_to_job * 4)) 
        num_phases = value
        timeline_str = f"{value} Week(s)"
    # Handle standard timelines
    else:
        unit = "Month"
        value = max(1, int(time_to_job))
        num_phases = min(value, 12) # Cap at 12 to maintain API speed
        timeline_str = f"{value} Month(s)"

    # BULLETPROOF STRING
    prompt_template = """
    Generate an aggressive career preparation roadmap for a candidate targeting a [TARGET] role.
    Time available: [TIMELINE]. Current Skills: [SKILLS].
    
    CRITICAL INSTRUCTIONS: 
    - Provide EXACTLY [PHASES] phases. 
    - Because the time available is [TIMELINE], do NOT write phases that take "Weeks" or "Months" if they only have days.
    
    Output ONLY a strict JSON object matching this exact structure:
    {"roadmap": [{"phase": "[UNIT] 1", "focus": "Topic", "actions": "Steps"}]}
    """
    
    prompt = prompt_template.replace("[TARGET]", str(target_tier)) \
                            .replace("[TIMELINE]", timeline_str) \
                            .replace("[UNIT]", str(unit)) \
                            .replace("[SKILLS]", ", ".join(skill_list)) \
                            .replace("[PHASES]", str(num_phases))
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content).get("roadmap", [])
    except Exception as e:
        print(f"Error generating roadmap: {e}")
        return []