"""Agent 4: Response Planner.

Generates a prioritized action plan grounded in the retrieved knowledge
base passages, the situation facts, and the risk assessment.
"""

import json

from services.llm_service import call_llm_json

SYSTEM_PROMPT = """You are the Response Planner agent inside ResQ-AI, an AI decision-support \
system for emergency response coordination used by human coordinators. You do NOT dispatch \
help, contact emergency services, or replace trained responders — you only propose a draft \
plan for humans to review and act on.

You will receive: structured situation facts, a risk assessment, and retrieved knowledge-base \
passages. Ground your plan in the retrieved passages where relevant. Respond with ONLY a JSON \
object (no prose, no markdown fences) matching this schema:

{
  "priority_actions": ["short, actionable, ordered step", ...],
  "response_plan": "3-6 sentence narrative plan covering evacuation, medical care, and resource needs as relevant",
  "considerations": ["resource, medical, or evacuation consideration to keep in mind", ...]
}

List 4-8 priority_actions ordered from most to least urgent. Be specific to the numbers and \
conditions given rather than generic."""


def _fallback_plan(situation: dict, risk: dict, knowledge: list) -> dict:
    """Deterministic rule-based fallback for offline demo mode."""
    emergency_type = situation.get("emergency_type", "other")
    affected = situation.get("affected_people", 0) or 0
    medical = situation.get("medical_cases", 0) or 0
    risk_level = risk.get("risk_level", "MEDIUM")

    actions = []
    if medical > 0:
        actions.append(
            f"Establish a medical triage point and prioritize the {medical} reported case(s) "
            f"using ABCs and bleeding control first"
        )
    if emergency_type == "flood":
        actions.append("Move stranded individuals to higher ground / stable elevated structures immediately")
        actions.append("Cut electrical power to affected structures where it is safe to do so")
        actions.append("Avoid crossing moving flood water; deploy boats or high-clearance vehicles if needed")
    elif emergency_type == "earthquake":
        actions.append("Direct people to open assembly points away from damaged structures and power lines")
        actions.append("Perform light search-and-rescue (shout-listen-tap) only in accessible, stable rubble")
        actions.append("Watch for gas leaks, downed lines, and aftershocks before allowing re-entry")
    elif emergency_type == "fire":
        actions.append("Evacuate the fire's projected path and move people upwind of smoke plumes")
        actions.append("Do not allow re-entry into burning or smoke-filled structures")
        actions.append("Monitor wind direction/speed to reassess evacuation zone boundaries")
    else:
        actions.append("Establish a safe assembly point and begin a headcount of affected individuals")

    if affected >= 50:
        actions.append(f"Coordinate evacuation transport and shelter capacity for approximately {affected} people")
    actions.append("Set up a registration/headcount point at the assembly area or shelter for accountability")
    actions.append("Establish clean water, sanitation, and basic supplies at the shelter location")
    actions.append("Maintain communication with local emergency management for resupply and status updates")

    plan_sentence_1 = (
        f"This {risk_level.lower()}-risk {emergency_type} scenario involves an estimated {affected} "
        f"affected people and {medical} medical case(s)."
    )
    plan_sentence_2 = (
        "Immediate priority is stabilizing medical cases and moving people out of the direct hazard zone, "
        "followed by establishing an accountable shelter location with water, sanitation, and basic supplies."
    )
    plan_sentence_3 = (
        "Coordinate with local emergency authorities for specialized resources (medical teams, heavy rescue, "
        "or firefighting units) rather than relying solely on bystander action."
    )
    response_plan = f"{plan_sentence_1} {plan_sentence_2} {plan_sentence_3}"

    considerations = [
        "Reassess conditions periodically since disaster situations evolve quickly",
        "Flag vulnerable individuals (children, elderly, disabled, chronic illness) for closer monitoring",
        "Do not send untrained bystanders into unstable or hazardous areas",
    ]

    return {
        "priority_actions": actions[:8],
        "response_plan": response_plan,
        "considerations": considerations,
    }


def generate_plan(situation: dict, risk: dict, knowledge: list) -> dict:
    """Runs the Response Planner agent."""
    user_prompt = json.dumps(
        {
            "situation": situation,
            "risk_assessment": risk,
            "retrieved_knowledge": knowledge,
        }
    )
    result = call_llm_json(SYSTEM_PROMPT, user_prompt, max_tokens=1500)
    if result["data"] is not None:
        data = result["data"]
        data.setdefault("priority_actions", [])
        data.setdefault("response_plan", "")
        data.setdefault("considerations", [])
        return {"data": data, "mode": result["mode"]}

    return {"data": _fallback_plan(situation, risk, knowledge), "mode": "demo"}
