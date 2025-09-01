# --- Utils ---
def validate_analysis(result: dict) -> dict:
    required_sections = ["Skills", "Education", "Job Role", "Experience"]
    validated = {}

    for section in required_sections:
        validated[section] = {
            "match_pct": result.get(section, {}).get("match_pct", 0),
            "resume_value": result.get(section, {}).get("resume_value", ""),
            "job_description_value": result.get(section, {}).get("job_description_value", ""),
            "explanation": result.get(section, {}).get("explanation", "No explanation available"),
        }

    validated["OverallMatchPercentage"] = result.get("OverallMatchPercentage", 0)
    validated["why_overall_match_is_this"] = result.get(
        "why_overall_match_is_this", "Not provided"
    )
    validated["AI_Generated_Estimate_Percentage"] = result.get(
        "AI_Generated_Estimate_Percentage", 0
    )

    return validated