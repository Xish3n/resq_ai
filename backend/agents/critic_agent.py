"""Agent 5: Critic Agent.

Reviews the generated response plan for missing risks, unsafe assumptions,
or gaps, and suggests corrections. This is what makes ResQ-AI a multi-agent
system rather than a single generate-and-return pipeline.
"""

import json

from services.llm_service import call_llm_json

SYSTEM_PROMPT = """You are the Critic agent inside ResQ-AI, an AI decision-support system for \
emergency response coordination. Your job is to critically review a draft response plan \
produced by another agent, NOT to write a new plan from scratch.

You will receive the situation facts, risk assessment, retrieved knowledge, and the draft plan \
as JSON. Respond with ONLY a JSON object (no prose, no markdown fences) matching this schema:

{
  "missing_risks": ["risk or hazard the draft plan did not adequately address", ...],
  "unsafe_assumptions": ["assumption in the draft plan that may not hold, or that could be unsafe if wrong", ...],
  "corrections": ["specific, actionable correction or addition to the plan", ...],
  "overall_assessment": "1-3 sentence overall verdict on the plan's soundness"
}

If the draft plan is already reasonably sound, it is fine to return short or empty lists for \
missing_risks and unsafe_assumptions, but always give at least one corrections item that \
would make the plan safer or more complete, and always remind that professional emergency \
services should be engaged for anything beyond immediate first response."""


def _fallback_critique(situation: dict, risk: dict, plan: dict) -> dict:
    """Deterministic rule-based fallback for offline demo mode."""
    emergency_type = situation.get("emergency_type", "other")
    medical = situation.get("medical_cases", 0) or 0
    risk_level = risk.get("risk_level", "MEDIUM")

    missing_risks = []
    unsafe_assumptions = []
    corrections = [
        "Confirm real-time status with local emergency services before executing any step of this plan"
    ]

    plan_text = json.dumps(plan).lower()

    if medical > 0 and "triage" not in plan_text:
        missing_risks.append("Draft plan does not explicitly reference medical triage prioritization")
        corrections.append("Add explicit triage categorization (immediate/delayed/minor) for medical cases")

    if emergency_type == "earthquake" and "aftershock" not in plan_text:
        missing_risks.append("Aftershock risk during ongoing search-and-rescue is not addressed")

    if emergency_type == "fire" and "wind" not in plan_text:
        missing_risks.append("Wind-driven fire spread and shifting smoke direction not addressed")

    if emergency_type == "flood" and "electric" not in plan_text and "power" not in plan_text:
        missing_risks.append("Electrocution risk from submerged electrical systems not addressed")

    if "communication" not in plan_text and "coordinat" not in plan_text:
        unsafe_assumptions.append("Plan assumes responders can act independently without confirming coordination with local authorities")

    if risk_level in ("HIGH", "CRITICAL") and "professional" not in plan_text and "authorit" not in plan_text:
        unsafe_assumptions.append("High-severity plan does not explicitly state that professional emergency services must be engaged")

    corrections.append("Reassess the situation every 15-30 minutes since conditions in active emergencies change quickly")

    overall_assessment = (
        f"The draft plan covers the core actions for a {risk_level.lower()}-risk {emergency_type} scenario, "
        f"but should be treated as a starting point for trained responders rather than a final instruction set."
    )

    return {
        "missing_risks": missing_risks or ["No major gaps identified in the draft plan"],
        "unsafe_assumptions": unsafe_assumptions or ["No clearly unsafe assumptions identified"],
        "corrections": corrections,
        "overall_assessment": overall_assessment,
    }


def critique_plan(situation: dict, risk: dict, knowledge: list, plan: dict) -> dict:
    """Runs the Critic agent against the draft plan."""
    user_prompt = json.dumps(
        {
            "situation": situation,
            "risk_assessment": risk,
            "retrieved_knowledge": knowledge,
            "draft_plan": plan,
        }
    )
    result = call_llm_json(SYSTEM_PROMPT, user_prompt, max_tokens=1000)
    if result["data"] is not None:
        data = result["data"]
        data.setdefault("missing_risks", [])
        data.setdefault("unsafe_assumptions", [])
        data.setdefault("corrections", [])
        data.setdefault("overall_assessment", "")
        return {"data": data, "mode": result["mode"]}

    return {"data": _fallback_critique(situation, risk, plan), "mode": "demo"}
