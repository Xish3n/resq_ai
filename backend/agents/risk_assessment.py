"""Agent 2: Risk Assessment.

Identifies risks and assigns an overall risk level (LOW/MEDIUM/HIGH/CRITICAL)
based on the structured situation data.
"""

from services.llm_service import call_llm_json

SYSTEM_PROMPT = """You are the Risk Assessment agent inside ResQ-AI, an AI decision-support \
system for emergency response coordination. You do NOT dispatch help or replace emergency \
authorities.

Given structured facts about an emergency situation (as JSON), identify risks and assign a \
risk level. Respond with ONLY a JSON object (no prose, no markdown fences) matching this schema:

{
  "risks": ["short risk description", ...],
  "risk_level": "one of: LOW, MEDIUM, HIGH, CRITICAL",
  "explanation": "2-4 sentences explaining why this risk level was chosen, referencing the specific numbers and conditions given"
}

Guidance for calibrating risk_level:
- CRITICAL: multiple medical cases needing urgent care, large affected population, and/or life-threatening hazards (structural collapse, active fire spread, deep fast water).
- HIGH: meaningful medical needs or hazardous conditions with a sizeable affected population.
- MEDIUM: some risk factors present but limited in scale or severity.
- LOW: small scale, no medical cases, minimal hazard conditions."""


def _fallback_assess(situation: dict) -> dict:
    """Deterministic rule-based fallback for offline demo mode."""
    affected = situation.get("affected_people", 0) or 0
    medical = situation.get("medical_cases", 0) or 0
    conditions = situation.get("conditions", []) or []
    emergency_type = situation.get("emergency_type", "other")

    severe_condition_hits = sum(
        1
        for c in conditions
        if any(
            kw in c.lower()
            for kw in ["trapped", "gas leak", "smoke inhalation", "injur", "blocked access"]
        )
    )

    score = 0
    score += 3 if medical >= 5 else (2 if medical >= 1 else 0)
    score += 3 if affected >= 200 else (2 if affected >= 50 else (1 if affected >= 10 else 0))
    score += min(severe_condition_hits, 2)
    if emergency_type in ("earthquake", "fire"):
        score += 1

    if score >= 7:
        risk_level = "CRITICAL"
    elif score >= 5:
        risk_level = "HIGH"
    elif score >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    risks = []
    if medical > 0:
        risks.append(f"{medical} people require medical attention; delays could worsen outcomes")
    if affected >= 50:
        risks.append(f"Large affected population ({affected}) strains evacuation and shelter capacity")
    for c in conditions:
        if "no additional hazard" not in c:
            risks.append(c.capitalize())
    if emergency_type == "fire":
        risks.append("Fire and smoke can spread rapidly, expanding the danger zone")
    if emergency_type == "earthquake":
        risks.append("Aftershocks may cause further structural collapse")
    if emergency_type == "flood":
        risks.append("Rising or fast-moving water increases drowning and contamination risk")
    if not risks:
        risks.append("No major additional risks identified beyond the primary incident")

    explanation = (
        f"Risk level set to {risk_level} based on an estimated {affected} affected people, "
        f"{medical} medical case(s), and {len(conditions)} notable condition(s) "
        f"in a {emergency_type} scenario. "
        f"{'Multiple compounding factors elevate urgency.' if score >= 5 else 'Compounding factors appear limited at this time.'}"
    )

    return {"risks": risks, "risk_level": risk_level, "explanation": explanation}


def assess_risk(situation: dict) -> dict:
    """Runs the Risk Assessment agent given the situation-analyzer output."""
    import json

    user_prompt = json.dumps(situation)
    result = call_llm_json(SYSTEM_PROMPT, user_prompt)
    if result["data"] is not None:
        data = result["data"]
        data.setdefault("risks", [])
        data.setdefault("risk_level", "MEDIUM")
        data.setdefault("explanation", "")
        if data["risk_level"] not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            data["risk_level"] = "MEDIUM"
        return {"data": data, "mode": result["mode"]}

    return {"data": _fallback_assess(situation), "mode": "demo"}
