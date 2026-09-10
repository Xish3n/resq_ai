# ResQ-AI

**Multi-Agent Generative AI Emergency Response & Decision Support System**

ResQ-AI takes a free-text emergency description (e.g. *"Heavy flooding has affected an area.
Around 100 people are stranded and 5 people need medical assistance."*) and runs it through a
pipeline of specialized AI agents to produce a structured, risk-assessed, knowledge-grounded,
peer-reviewed draft response plan for a human coordinator.

> **ResQ-AI is a decision-support prototype.** It never contacts emergency services, dispatches
> responders, or claims to give professional medical/fire/police/rescue instructions. Every
> output is a draft for human review — see the in-app disclaimer.

---

## 1. Architecture

```
User Input (free text)
      │
      ▼
┌─────────────────────┐
│ 1. Situation         │  Extracts emergency type, affected people,
│    Analyzer          │  medical cases, and notable conditions.
└─────────┬────────────┘
      ▼
┌─────────────────────┐
│ 2. Risk Assessment    │  Identifies risks, assigns LOW/MEDIUM/HIGH/
│    Agent              │  CRITICAL, explains the reasoning.
└─────────┬────────────┘
      ▼
┌─────────────────────┐
│ 3. RAG Knowledge      │  Embeds a query from the situation + risks,
│    Agent              │  retrieves relevant guideline passages from a
│                       │  local vector store (FAISS + MiniLM).
└─────────┬────────────┘
      ▼
┌─────────────────────┐
│ 4. Response Planner   │  Drafts prioritized actions + a narrative
│    Agent              │  plan, grounded in the retrieved knowledge.
└─────────┬────────────┘
      ▼
┌─────────────────────┐
│ 5. Critic Agent       │  Reviews the draft plan for missing risks,
│                       │  unsafe assumptions, and corrections.
└─────────┬────────────┘
      ▼
┌─────────────────────┐
│ 6. Final Response     │  Assembles everything + mandatory
│    Agent              │  decision-support disclaimer.
└─────────┬────────────┘
      ▼
 Structured JSON → React Dashboard
```

Each agent is a small, focused function (not an open-ended autonomous loop) that either:
- calls the LLM (Anthropic API) with a strict "return only JSON" system prompt, or
- if no API key is configured, the key is invalid, or the network is unavailable, transparently
  falls back to a deterministic, rule-based implementation ("offline demo mode") so the app
  **always produces a complete result during a live demo**.

The UI shows which mode each stage ran in, so judges can see the real architecture at work
either way.

### RAG layer

- Knowledge base: 6 plain-text documents in `backend/data/` covering flood safety, earthquake
  response, fire safety, evacuation procedures, medical triage, and shelter/resource management.
- Embeddings: `sentence-transformers` (`all-MiniLM-L6-v2`) + `faiss` cosine/IP similarity search.
- If those libraries or their model weights aren't available offline, the retriever
  automatically falls back to a TF-IDF (`scikit-learn`) similarity search over the same chunks —
  same interface, no code changes needed elsewhere in the app.

### LLM layer

- Uses the **Anthropic API** (`anthropic` Python SDK) with the model set via `ANTHROPIC_MODEL`
  in `.env` (defaults to `claude-sonnet-4-6`).
- Every agent prompt requests strict JSON output, which is parsed defensively (handles stray
  markdown fences, retries JSON extraction from surrounding text).
- No API key → **offline demo mode** automatically, using clearly-labeled rule-based logic
  instead of fabricated "fake AI" text.

---

## 2. Folder structure

```
resq-ai/
├── backend/
│   ├── main.py                    # FastAPI app, routes
│   ├── orchestrator.py            # Runs the 6-agent pipeline in order
│   ├── agents/
│   │   ├── situation_analyzer.py
│   │   ├── risk_assessment.py
│   │   ├── rag_agent.py
│   │   ├── response_planner.py
│   │   ├── critic_agent.py
│   │   └── final_response.py
│   ├── rag/
│   │   └── retriever.py           # FAISS/MiniLM + TF-IDF fallback
│   ├── services/
│   │   └── llm_service.py         # Anthropic API wrapper + demo-mode fallback
│   ├── data/                      # RAG knowledge base (.txt)
│   │   ├── flood_safety.txt
│   │   ├── earthquake_response.txt
│   │   ├── fire_safety.txt
│   │   ├── evacuation_procedures.txt
│   │   ├── medical_triage.txt
│   │   └── shelter_resource_management.txt
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── api.js
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── InputPanel.jsx
│   │       ├── ScenarioButtons.jsx
│   │       ├── PipelineTrace.jsx
│   │       ├── Dashboard.jsx
│   │       ├── RiskBadge.jsx
│   │       ├── SectionPanel.jsx
│   │       └── Disclaimer.jsx
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── vite.config.js
│   └── .env.example
│
├── .gitignore
└── README.md   (this file)
```

---

## 3. Setup & run instructions (Windows)

### Prerequisites
- Python 3.10+ installed and on PATH
- Node.js 18+ and npm installed
- (Optional but recommended) An Anthropic API key for live LLM mode

### Backend (PowerShell or cmd)

```bat
cd resq-ai\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` in a text editor and paste your key:

```
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-6
ALLOWED_ORIGINS=http://localhost:5173
```

If you don't have a key, leave `ANTHROPIC_API_KEY` blank — the app will automatically run in
offline demo mode.

Run the API:

```bat
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`. Check `http://localhost:8000/api/health`.

> Note: the first run will attempt to download the `all-MiniLM-L6-v2` embedding model
> (~80MB) for the RAG layer. If there is no internet access at your venue, the retriever
> automatically falls back to a TF-IDF search over the same knowledge base — no setup
> changes required.

### Frontend (new terminal window)

```bat
cd resq-ai\frontend
npm install
copy .env.example .env
npm run dev
```

Open the printed local URL (default `http://localhost:5173`).

### Quick sanity check

1. Visit the frontend.
2. Click one of the four example scenario buttons (Flood / Earthquake / Fire / Medical).
3. Click "Analyze emergency".
4. You should see the full dashboard populate: emergency type, risk level, affected people,
   medical cases, detected risks, priority actions, response plan, retrieved knowledge sources,
   critic review, and the disclaimer.

---

## 4. Two-minute hackathon demo script

**0:00 – 0:15 | Hook**
> "In a real emergency, the first responder or coordinator doesn't need another chatbot — they
> need structured, risk-ranked, source-grounded guidance in seconds. That's ResQ-AI."

**0:15 – 0:35 | Show the input**
- Open the dashboard. Point out the clean input box and the four example scenario buttons.
- Click **Flood**. Show the pre-filled realistic scenario text.

**0:35 – 1:05 | Run it and narrate the pipeline**
- Click **Analyze emergency**.
- While it loads, point at the **agent pipeline trace bar**: "This isn't one prompt — it's six
  cooperating agents: Situation Analyzer, Risk Assessment, RAG Retrieval, Response Planner,
  Critic Agent, and Final Response."
- Results land: point out the **Risk Level badge** (color-coded LOW→CRITICAL), **affected
  people / medical cases** stat tiles.

**1:05 – 1:30 | Show the depth**
- Scroll to **Detected Risks & AI Explanation** — explain the model isn't just guessing, it's
  explaining *why* this is HIGH/CRITICAL.
- Scroll to **Retrieved Knowledge & Sources** — "This isn't hallucinated advice — it's grounded
  in our RAG knowledge base of real emergency-response guidelines, retrieved via FAISS
  embedding search, with the source document shown."

**1:30 – 1:50 | The differentiator: Critic Agent**
- Scroll to **Critic Agent Review**: "Most GenAI demos stop at 'generate a plan.' ResQ-AI has a
  second agent whose only job is to red-team the first plan — flagging missing risks and unsafe
  assumptions before a human ever sees it."

**1:50 – 2:00 | Close**
- Point at the disclaimer: "And critically — this is decision *support*. It never pretends to
  contact emergency services or replace trained responders. It makes the humans in the loop
  faster and better-informed."

---

## 5. Why ResQ-AI is different from "just a chatbot"

A generic chatbot takes a prompt and returns one blob of text, with no guarantee of structure,
no fact-grounding, and no self-checking. ResQ-AI is architected differently:

1. **Decomposed multi-agent reasoning, not one giant prompt.** Each agent has one narrow job
   (extract facts / assess risk / retrieve knowledge / plan / critique), which produces more
   reliable, auditable, and debuggable output than a single "do everything" prompt — and lets
   each stage be inspected independently (as the pipeline trace bar shows live).
2. **Retrieval-grounded, not hallucinated.** The response plan is built on top of passages
   actually retrieved from a curated emergency-guidelines knowledge base via embedding search,
   with the source document shown — not the model's unverified "memory."
3. **Self-critique built into the architecture.** The Critic Agent is a second, independent
   pass that actively looks for gaps and unsafe assumptions in the first plan, mirroring how
   real incident command uses a second reviewer rather than trusting the first draft.
4. **Structured decision-support output, not prose.** Risk level, affected counts, prioritized
   actions, and sources are all separately structured fields a coordinator can scan in seconds
   under time pressure — not a paragraph they have to parse.
5. **Fails safely.** If the LLM or embedding model is unavailable, the system degrades to a
   transparent, clearly-labeled rule-based mode rather than silently failing or fabricating
   plausible-sounding nonsense.

---

## 6. Likely judge questions & strong answers

**Q1: "What happens if the LLM API is down or you don't have internet at the venue?"**
> "ResQ-AI has a graceful degradation path built into every layer. If there's no API key, the
> request fails, or the embedding model can't download, each agent falls back to a
> deterministic, rule-based implementation — and the UI clearly labels which mode each stage
> ran in. Nothing is faked; the fallback logic is real, inspectable code, just less flexible
> than the LLM. It also means the demo never breaks live."

**Q2: "How do you know the model isn't hallucinating the emergency guidance?"**
> "The Response Planner agent is given the actual retrieved passages from our knowledge base as
> context and instructed to ground its plan in them, and we surface those exact passages with
> their source document in the UI so a human can verify the plan against the source. We also
> added a Critic Agent as a second independent check specifically to catch unsupported or risky
> claims before they reach the final output."

**Q3: "Why six agents instead of one well-crafted prompt?"**
> "A single prompt has to balance extraction, risk judgment, retrieval, planning, and
> self-review all at once, which in practice makes it more prone to skipping steps under time
> pressure. Splitting it into narrow agents means each step is independently testable, the
> intermediate state is inspectable — you literally see the pipeline light up stage by stage —
> and we can swap out or improve one stage (say, the risk model) without touching the rest."

**Q4: "Is this meant to actually replace 911 / emergency call centers?"**
> "No — explicitly not. ResQ-AI never contacts emergency services and states in the UI, every
> time, that it's a decision-support prototype for human coordinators to review, not a
> replacement for professional responders. Its job is to compress the first few minutes of
> situational triage into a structured brief, not to make the call."

**Q5: "How would this scale beyond a hackathon demo?"**
> "The architecture is already modular enough to extend: the knowledge base is just text files
> today, but could ingest official agency PDFs; the LLM calls could route to specialized
> fine-tuned models per agent; and the orchestrator could add agents for resource-dispatch
> optimization or multi-incident prioritization. The FastAPI backend and stateless JSON contract
> mean the same pipeline could sit behind a call-center tool, a mobile app for field responders,
> or an integration into existing emergency-management software."

---

## Notes & limitations

- This is a hackathon MVP: it does not persist history in a database by default (add SQLite in
  `backend/services` if you need to log past analyses), does not authenticate users, and the
  rule-based fallback logic, while sensible, is intentionally simple.
- All emergency-response content in `backend/data/` is condensed general guidance for
  demonstration purposes, not official agency doctrine — real deployments should replace it
  with vetted, agency-approved source material.
