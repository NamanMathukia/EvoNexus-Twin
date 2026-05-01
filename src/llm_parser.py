"""
src/llm_parser.py
Uses Groq (Llama 3.1) to parse raw resume text into the ENT feature dictionary.
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load the .env file automatically
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def parse_resume_to_features(resume_text: str) -> dict:
    """Passes resume text to Groq and forces a strict JSON output."""
    
    system_prompt = """
    You are an expert technical recruiter AI evaluating a student for placement.
    Read the provided resume/profile text and extract the candidate's metrics into strict JSON.
    DO NOT output markdown, conversational text, or anything other than the JSON object.
    
    Follow this exact JSON schema and guess reasonably if data is missing:
    {
      "cgpa": 7.5,                  // float (estimate out of 10.0)
      "skills": 0.6,                // float 0.0 to 1.0 (overall technical depth)
      "skill_list": ["Python", "AWS", "SQL"], // list of string skills found
      "internship": 1,              // 1 if they have internship experience, 0 if not
      "internship_quality": 0.8,    // float 0.0 to 1.0
      "academic_consistency": 0.7,  // float 0.0 to 1.0
      "portal_activity": 0.5,       // float 0.0 to 1.0 (guess 0.5 if unknown)
      "resume_updates": 2,          // int (guess 2 if unknown)
      "interviews": 3,              // int (count of past roles/projects as proxy)
      "skill_demand_score": 0.8,    // float 0.0 to 1.0 (based on AI/Cloud trends)
      "market_demand": 0.7          // float 0.0 to 1.0
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
        
        result_json = response.choices[0].message.content
        return json.loads(result_json)
        
    except Exception as e:
        print(f"Error parsing resume: {e}")
        # Fallback dictionary to prevent demo crashes
        return {
            "cgpa": 7.0, "skills": 0.3, "skill_list": ["Python"],
            "internship": 0, "internship_quality": 0.0, "academic_consistency": 0.7,
            "portal_activity": 0.5, "resume_updates": 1, "interviews": 1,
            "skill_demand_score": 0.5, "market_demand": 0.5
        }