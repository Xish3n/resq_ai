import React from "react";

const STAGES = [
  { key: "situation_analyzer", label: "Situation Analyzer" },
  { key: "risk_assessment", label: "Risk Assessment" },
  { key: "rag_backend", label: "RAG Retrieval" },
  { key: "response_planner", label: "Response Planner" },
  { key: "critic_agent", label: "Critic Agent" },
];

export default function PipelineTrace({ modes, loading }) {
  return (
    <div className="rounded-lg border border-base-600 bg-base-800/50 px-5 py-4">
      <p className="mb-3 text-[15px] font-semibold text-ink-300">Agent pipeline</p>
      <div className="flex flex-wrap items-center gap-x-1 gap-y-3">
        {STAGES.map((stage, i) => {
          const mode = modes ? modes[stage.key] : null;
          const isLive = mode === "live" || mode === "faiss+minilm";
          const isDone = Boolean(mode) && !loading;
          const isActive = loading && !modes;
          return (
            <React.Fragment key={stage.key}>
              <div
                className={`flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs font-mono transition-colors
                  ${
                    isDone
                      ? isLive
                        ? "border-risk-low/40 bg-risk-low/10 text-risk-low"
                        : "border-signal-amber/40 bg-signal-amber/10 text-signal-amber"
                      : "border-base-600 bg-base-900 text-ink-700"
                  }`}
              >
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    isDone ? (isLive ? "bg-risk-low" : "bg-signal-amber") : isActive ? "bg-signal-cyan pulse-dot" : "bg-base-500"
                  }`}
                />
                {stage.label}
              </div>
              {i < STAGES.length - 1 && (
                <span className="text-ink-700 text-xs">→</span>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
