"""Agent 3: RAG Knowledge Agent.

Retrieves relevant emergency-guideline passages from the local knowledge
base to ground the response plan in real reference material.
"""

from rag.retriever import retriever

_SOURCE_LABELS = {
    "flood_safety": "Flood Safety and Response Guidelines",
    "earthquake_response": "Earthquake Response Guidelines",
    "fire_safety": "Fire Emergency Response Guidelines",
    "evacuation_procedures": "General Evacuation Procedures",
    "medical_triage": "Emergency Medical Triage Priorities",
    "shelter_resource_management": "Shelter and Resource Management Guidelines",
}


def retrieve_knowledge(situation: dict, risk: dict, top_k: int = 4) -> dict:
    """Builds a query from the situation + risk data and retrieves supporting docs."""
    emergency_type = situation.get("emergency_type", "")
    conditions = " ".join(situation.get("conditions", []) or [])
    risks = " ".join(risk.get("risks", []) or [])
    medical = situation.get("medical_cases", 0) or 0

    query_parts = [emergency_type, situation.get("summary", ""), conditions, risks]
    if medical > 0:
        query_parts.append("medical triage priorities injuries")
    query = " ".join(p for p in query_parts if p)

    raw_results = retriever.retrieve(query, top_k=top_k)

    results = []
    for r in raw_results:
        results.append(
            {
                "source": _SOURCE_LABELS.get(r["source"], r["source"]),
                "text": r["text"],
                "relevance_score": round(r["score"], 3),
            }
        )

    return {
        "data": results,
        "backend": retriever.backend,
        "query_used": query,
    }
