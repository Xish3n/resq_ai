"""Agent 6: Final Response Agent.

Assembles the outputs of all upstream agents into the final structured
response returned to the frontend, and attaches the mandatory disclaimer.
"""

DISCLAIMER = (
    "ResQ-AI is an AI decision-support prototype built for demonstration purposes. "
    "It does NOT contact emergency services, dispatch responders, or provide professional "
    "medical, fire, police, or rescue instructions. All outputs are AI-generated suggestions "
    "for human coordinators to review, verify, and act on at their own judgment. In a real "
    "emergency, always contact your local emergency services immediately."
)


def build_final_response(
    description: str,
    situation: dict,
    risk: dict,
    knowledge: list,
    plan: dict,
    critique: dict,
    modes: dict,
) -> dict:
    """Combines all agent outputs into the final API response payload."""
    return {
        "input_description": description,
        "emergency_type": situation.get("emergency_type", "other"),
        "affected_people": situation.get("affected_people", 0),
        "medical_cases": situation.get("medical_cases", 0),
        "conditions": situation.get("conditions", []),
        "situation_summary": situation.get("summary", ""),
        "risk_level": risk.get("risk_level", "MEDIUM"),
        "detected_risks": risk.get("risks", []),
        "risk_explanation": risk.get("explanation", ""),
        "priority_actions": plan.get("priority_actions", []),
        "response_plan": plan.get("response_plan", ""),
        "considerations": plan.get("considerations", []),
        "retrieved_knowledge": knowledge,
        "critic_review": {
            "missing_risks": critique.get("missing_risks", []),
            "unsafe_assumptions": critique.get("unsafe_assumptions", []),
            "corrections": critique.get("corrections", []),
            "overall_assessment": critique.get("overall_assessment", ""),
        },
        "disclaimer": DISCLAIMER,
        "agent_modes": modes,
    }
