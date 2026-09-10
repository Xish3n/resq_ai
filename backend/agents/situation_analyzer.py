"""Agent 1: Situation Analyzer.

Extracts structured facts from the free-text emergency description:
emergency type, affected population, medical cases, and notable conditions.
"""

import re

from services.llm_service import call_llm_json

SYSTEM_PROMPT = """You are the Situation Analyzer agent inside ResQ-AI, an AI decision-support \
system for emergency response coordination. You do NOT dispatch help or replace emergency \
authorities; you only structure information for human responders.

Given a free-text emergency description, extract structured facts. Respond with ONLY a JSON \
object (no prose, no markdown fences) matching this schema:

{
  "emergency_type": "one of: flood, earthquake, fire, medical, storm, other",
  "affected_people": <integer estimate, 0 if unknown>,
  "medical_cases": <integer estimate of people needing medical attention, 0 if none mentioned>,
  "conditions": ["short phrase describing a notable condition or hazard mentioned in the text", ...],
  "summary": "one clear sentence summarizing the situation"
}

Be conservative and evidence-based: only report numbers and conditions actually implied by the text."""


_TYPE_KEYWORDS = {
    "flood": ["flood", "flooding", "water level", "submerged", "overflow", "river burst"],
    "earthquake": ["earthquake", "quake", "tremor", "collapsed building", "aftershock", "rubble"],
    "fire": ["fire", "wildfire", "blaze", "smoke", "burning"],
    "medical": ["medical emergency", "outbreak", "poisoning", "mass casualty", "collapsed and", "unconscious"],
    "storm": ["storm", "hurricane", "cyclone", "tornado", "typhoon"],
}


def _fallback_analyze(text: str) -> dict:
    """Deterministic, transparent rule-based fallback for offline demo mode."""
    lowered = text.lower()

    emergency_type = "other"
    for etype, keywords in _TYPE_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            emergency_type = etype
            break

    # Mask decimal numbers (e.g. a "6.2" earthquake magnitude) before extracting integer
    # counts, so "6.2" is never misread as the separate integers 6 and 2.
    masked = re.sub(r"\b\d+\.\d+\b", "<decimal>", lowered)

    def _first_match(patterns):
        for pattern in patterns:
            m = re.search(pattern, masked)
            if m:
                return int(m.group(1).replace(",", ""))
        return None

    # Small tolerant gap (a few filler words, no other digits) between a number and its
    # anchor phrase, e.g. "3 people are already experiencing smoke inhalation".
    GAP = r"[a-z\s]{0,40}?"

    # Affected-population patterns, most specific/reliable first.
    affected_people = _first_match(
        [
            rf"(\d[\d,]{{0,6}})\s*(?:people|persons|residents|individuals|attendees){GAP}(?:affected|stranded|impacted)",
            r"approximately\s*(\d[\d,]{0,6})\s*(?:people|persons|residents|individuals)",
            r"around\s*(\d[\d,]{0,6})\s*(?:people|persons|residents|individuals|attendees)",
            rf"(\d[\d,]{{0,6}})\s*(?:people|persons|residents|individuals|attendees){GAP}(?:need|require|requiring)\s*(?:to\s+)?evacuat",
            r"(\d[\d,]{0,6})\s*(?:people|persons|residents|individuals|attendees)",
        ]
    )
    if affected_people is None:
        # Last resort: largest standalone (non-decimal) number in the text.
        fallback_numbers = [int(n.replace(",", "")) for n in re.findall(r"\b(\d[\d,]{0,6})\b", masked)]
        affected_people = max(fallback_numbers) if fallback_numbers else 0

    # Medical-need patterns, most specific/reliable first.
    medical_cases = _first_match(
        [
            rf"(\d[\d,]{{0,5}})\s*(?:people|persons|individuals|residents|attendees)?{GAP}(?:need|require|requiring|needing)\s*(?:urgent\s+)?medical",
            rf"(\d[\d,]{{0,5}})\s*(?:people|persons|individuals|residents|attendees)?{GAP}(?:visible\s+)?(?:injuries|injured|trauma)",
            rf"(\d[\d,]{{0,5}})\s*(?:people|persons|individuals)?{GAP}trapped",
            rf"(\d[\d,]{{0,5}})\s*(?:people|persons|individuals|attendees)?{GAP}collapsed",
            rf"(\d[\d,]{{0,5}})\s*(?:people|persons|individuals)?{GAP}(?:smoke inhalation|symptoms)",
        ]
    )
    if medical_cases is None:
        medical_cases = 0

    conditions = []
    condition_keywords = {
        "stranded": "people stranded and unable to self-evacuate",
        "trapped": "people trapped, possibly under debris or structures",
        "power": "power outage affecting the area",
        "gas leak": "possible gas leak hazard",
        "children": "children present among affected population",
        "elderly": "elderly individuals present among affected population",
        "no access": "limited or blocked access for responders",
        "night": "incident occurring at night, reducing visibility",
        "injured": "injuries reported among affected population",
        "smoke": "smoke inhalation hazard present",
    }
    for kw, desc in condition_keywords.items():
        if kw in lowered:
            conditions.append(desc)
    if not conditions:
        conditions.append("no additional hazard conditions explicitly stated")

    summary = (
        f"A {emergency_type} emergency affecting approximately {affected_people or 'an unspecified number of'} "
        f"people, with {medical_cases or 'no explicitly stated'} medical case(s) reported."
    )

    return {
        "emergency_type": emergency_type,
        "affected_people": affected_people,
        "medical_cases": medical_cases,
        "conditions": conditions,
        "summary": summary,
    }


def analyze_situation(description: str) -> dict:
    """Runs the Situation Analyzer agent. Returns dict + metadata about mode used."""
    result = call_llm_json(SYSTEM_PROMPT, description)
    if result["data"] is not None:
        data = result["data"]
        data.setdefault("emergency_type", "other")
        data.setdefault("affected_people", 0)
        data.setdefault("medical_cases", 0)
        data.setdefault("conditions", [])
        data.setdefault("summary", "")
        return {"data": data, "mode": result["mode"]}

    return {"data": _fallback_analyze(description), "mode": "demo"}
