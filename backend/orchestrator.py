"""Orchestrator: runs the ResQ-AI multi-agent pipeline in order.

User Input -> Situation Analyzer -> Risk Assessment -> RAG Retrieval
-> Response Planner -> Critic Agent -> Final Response
"""

from agents import (
    critic_agent,
    final_response,
    rag_agent,
    response_planner,
    risk_assessment,
    situation_analyzer,
)


def run_pipeline(description: str) -> dict:
    situation_result = situation_analyzer.analyze_situation(description)
    situation = situation_result["data"]

    risk_result = risk_assessment.assess_risk(situation)
    risk = risk_result["data"]

    knowledge_result = rag_agent.retrieve_knowledge(situation, risk)
    knowledge = knowledge_result["data"]

    plan_result = response_planner.generate_plan(situation, risk, knowledge)
    plan = plan_result["data"]

    critique_result = critic_agent.critique_plan(situation, risk, knowledge, plan)
    critique = critique_result["data"]

    modes = {
        "situation_analyzer": situation_result["mode"],
        "risk_assessment": risk_result["mode"],
        "rag_backend": knowledge_result["backend"],
        "response_planner": plan_result["mode"],
        "critic_agent": critique_result["mode"],
    }

    return final_response.build_final_response(
        description=description,
        situation=situation,
        risk=risk,
        knowledge=knowledge,
        plan=plan,
        critique=critique,
        modes=modes,
    )
