import React from "react";
import RiskBadge from "./RiskBadge.jsx";
import SectionPanel from "./SectionPanel.jsx";
import Disclaimer from "./Disclaimer.jsx";
import PipelineTrace from "./PipelineTrace.jsx";

const TYPE_LABELS = {
  flood: "Flood",
  earthquake: "Earthquake",
  fire: "Fire",
  medical: "Medical emergency",
  storm: "Storm",
  other: "Unclassified",
};

function StatTile({ label, value, mono = true }) {
  return (
    <div className="rounded-lg border border-base-600 bg-base-800/70 px-4 py-3.5">
      <p className="text-xs text-ink-500">{label}</p>
      <p className={`mt-1 text-xl font-semibold text-ink-100 ${mono ? "font-mono" : ""}`}>
        {value}
      </p>
    </div>
  );
}

export default function Dashboard({ result }) {
  if (!result) return null;

  const {
    emergency_type,
    risk_level,
    affected_people,
    medical_cases,
    conditions = [],
    situation_summary,
    detected_risks = [],
    risk_explanation,
    priority_actions = [],
    response_plan,
    considerations = [],
    retrieved_knowledge = [],
    critic_review = {},
    disclaimer,
    agent_modes,
  } = result;

  return (
    <div className="mt-8 flex flex-col gap-5 rise-in">
      <PipelineTrace modes={agent_modes} loading={false} />

      {/* Top stat row */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatTile label="Emergency type" value={TYPE_LABELS[emergency_type] || emergency_type} mono={false} />
        <div className="rounded-lg border border-base-600 bg-base-800/70 px-4 py-3.5">
          <p className="text-xs text-ink-500">Risk level</p>
          <div className="mt-1.5">
            <RiskBadge level={risk_level} />
          </div>
        </div>
        <StatTile label="Affected people" value={affected_people ?? "—"} />
        <StatTile label="Medical cases" value={medical_cases ?? "—"} />
      </div>

      {situation_summary && (
        <p className="text-[15px] leading-relaxed text-ink-300 border-l-2 border-base-600 pl-4">
          {situation_summary}
        </p>
      )}

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Detected risks + explanation */}
        <SectionPanel index="02" title="Detected risks & AI explanation" accent="critical">
          <ul className="space-y-2">
            {detected_risks.map((r, i) => (
              <li key={i} className="flex gap-2 text-[14px] text-ink-300">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-risk-critical" />
                {r}
              </li>
            ))}
          </ul>
          {risk_explanation && (
            <p className="mt-3 text-[13px] leading-relaxed text-ink-500 border-t border-base-600 pt-3">
              {risk_explanation}
            </p>
          )}
          {conditions.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {conditions.map((c, i) => (
                <span
                  key={i}
                  className="rounded border border-base-600 bg-base-900 px-2 py-1 text-[11px] font-mono text-ink-500"
                >
                  {c}
                </span>
              ))}
            </div>
          )}
        </SectionPanel>

        {/* Priority action plan */}
        <SectionPanel index="03" title="Priority action plan" accent="amber">
          <ol className="space-y-2.5">
            {priority_actions.map((action, i) => (
              <li key={i} className="flex gap-3 text-[14px] text-ink-100">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded bg-signal-amber/15 font-mono text-[11px] font-semibold text-signal-amber">
                  {i + 1}
                </span>
                {action}
              </li>
            ))}
          </ol>
        </SectionPanel>
      </div>

      {/* Response plan narrative */}
      {response_plan && (
        <SectionPanel index="04" title="Recommended response plan" accent="teal">
          <p className="text-[14px] leading-relaxed text-ink-300">{response_plan}</p>
          {considerations.length > 0 && (
            <div className="mt-4 border-t border-base-600 pt-3">
              <p className="mb-2 text-[13px] font-medium text-ink-500">Additional considerations</p>
              <ul className="space-y-1.5">
                {considerations.map((c, i) => (
                  <li key={i} className="flex gap-2 text-[13px] text-ink-500">
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-signal-teal" />
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </SectionPanel>
      )}

      <div className="grid gap-5 lg:grid-cols-2">
        {/* Retrieved knowledge */}
        <SectionPanel index="05" title="Retrieved knowledge & sources" accent="cyan">
          <div className="space-y-3">
            {retrieved_knowledge.map((k, i) => (
              <div key={i} className="rounded-md border border-base-600 bg-base-900/60 px-3.5 py-3">
                <div className="mb-1.5 flex items-center justify-between">
                  <p className="text-[12px] font-semibold text-signal-cyan">{k.source}</p>
                  <span className="font-mono text-[10px] text-ink-700">
                    relevance {k.relevance_score}
                  </span>
                </div>
                <p className="text-[13px] leading-relaxed text-ink-500 line-clamp-4">{k.text}</p>
              </div>
            ))}
            {retrieved_knowledge.length === 0 && (
              <p className="text-[13px] text-ink-700">No supporting passages retrieved.</p>
            )}
          </div>
        </SectionPanel>

        {/* Critic review */}
        <SectionPanel index="06" title="Critic agent review" accent="amber">
          <div className="space-y-3">
            {critic_review.overall_assessment && (
              <p className="text-[13px] leading-relaxed text-ink-300">
                {critic_review.overall_assessment}
              </p>
            )}
            {critic_review.missing_risks?.length > 0 && (
              <div>
                <p className="text-[12px] font-medium text-ink-500 mb-1">Missing risks flagged</p>
                <ul className="space-y-1">
                  {critic_review.missing_risks.map((m, i) => (
                    <li key={i} className="text-[13px] text-ink-300">• {m}</li>
                  ))}
                </ul>
              </div>
            )}
            {critic_review.unsafe_assumptions?.length > 0 && (
              <div>
                <p className="text-[12px] font-medium text-ink-500 mb-1">Unsafe assumptions</p>
                <ul className="space-y-1">
                  {critic_review.unsafe_assumptions.map((m, i) => (
                    <li key={i} className="text-[13px] text-ink-300">• {m}</li>
                  ))}
                </ul>
              </div>
            )}
            {critic_review.corrections?.length > 0 && (
              <div>
                <p className="text-[12px] font-medium text-ink-500 mb-1">Suggested corrections</p>
                <ul className="space-y-1">
                  {critic_review.corrections.map((m, i) => (
                    <li key={i} className="text-[13px] text-ink-300">• {m}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </SectionPanel>
      </div>

      {disclaimer && <Disclaimer text={disclaimer} />}
    </div>
  );
}
