"""ResQ-AI FastAPI backend entry point."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from orchestrator import run_pipeline
from services.llm_service import is_live_mode

load_dotenv()

app = FastAPI(
    title="ResQ-AI API",
    description="Multi-Agent Generative AI Emergency Response & Decision Support System",
    version="1.0.0",
)

allowed_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=5, max_length=4000)


EXAMPLE_SCENARIOS = {
    "flood": (
        "Heavy flooding has affected a low-lying residential area after continuous rainfall. "
        "Around 100 people are stranded on rooftops and upper floors, and 5 people need medical "
        "assistance including one elderly resident with breathing difficulty. Power lines in the "
        "area appear to be submerged and roads are impassable by normal vehicles."
    ),
    "earthquake": (
        "A magnitude 6.2 earthquake has struck a densely populated urban district. Several "
        "buildings have partially collapsed and approximately 250 people are affected. At least "
        "12 people are trapped under rubble and 20 people have visible injuries including "
        "suspected fractures. Gas leaks have been reported near two of the collapsed structures."
    ),
    "fire": (
        "A fast-moving wildfire is approaching a rural community of about 60 households. Wind "
        "speeds are increasing and shifting direction. Around 180 residents need to evacuate and "
        "3 people are already experiencing smoke inhalation symptoms. One elderly care home with "
        "15 non-ambulatory residents is in the projected path."
    ),
    "medical": (
        "A large public event has experienced a mass food poisoning incident. Around 40 "
        "attendees are showing symptoms of severe nausea, vomiting, and dehydration, and 8 "
        "people have collapsed and require urgent medical attention. On-site medical staff are "
        "overwhelmed and additional support has not yet arrived."
    ),
}


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "llm_mode": "live" if is_live_mode() else "demo",
    }


@app.get("/api/scenarios")
def get_scenarios():
    return EXAMPLE_SCENARIOS


@app.post("/api/analyze")
def analyze_emergency(payload: AnalyzeRequest):
    try:
        result = run_pipeline(payload.description)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline failed: {exc}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
