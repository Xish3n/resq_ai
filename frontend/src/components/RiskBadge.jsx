import React from "react";

const RISK_STYLES = {
  LOW: {
    label: "Low",
    text: "text-risk-low",
    bg: "bg-risk-low/10",
    border: "border-risk-low/40",
    dot: "bg-risk-low",
  },
  MEDIUM: {
    label: "Medium",
    text: "text-risk-medium",
    bg: "bg-risk-medium/10",
    border: "border-risk-medium/40",
    dot: "bg-risk-medium",
  },
  HIGH: {
    label: "High",
    text: "text-risk-high",
    bg: "bg-risk-high/10",
    border: "border-risk-high/40",
    dot: "bg-risk-high",
  },
  CRITICAL: {
    label: "Critical",
    text: "text-risk-critical",
    bg: "bg-risk-critical/10",
    border: "border-risk-critical/40",
    dot: "bg-risk-critical",
  },
};

export default function RiskBadge({ level, size = "md" }) {
  const style = RISK_STYLES[level] || RISK_STYLES.MEDIUM;
  const sizing = size === "lg" ? "text-2xl px-5 py-2.5" : "text-sm px-3 py-1";

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-md border font-mono font-semibold tracking-wide ${style.bg} ${style.border} ${style.text} ${sizing}`}
    >
      <span className={`h-2 w-2 rounded-full ${style.dot} ${level === "CRITICAL" ? "pulse-dot" : ""}`} />
      {style.label}
    </span>
  );
}
