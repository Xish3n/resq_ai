import React from "react";

export default function SectionPanel({ index, title, accent = "cyan", children, className = "" }) {
  const accentMap = {
    cyan: "before:bg-signal-cyan",
    amber: "before:bg-signal-amber",
    teal: "before:bg-signal-teal",
    critical: "before:bg-risk-critical",
  };

  return (
    <div
      className={`relative rounded-lg border border-base-600 bg-base-800/70 pl-5 pr-5 py-5 shadow-panel
        before:absolute before:left-0 before:top-0 before:h-full before:w-[3px] before:rounded-l-lg ${accentMap[accent]} ${className}`}
    >
      <div className="mb-3 flex items-center gap-2">
        {index && (
          <span className="font-mono text-xs text-ink-700">{index}</span>
        )}
        <h3 className="text-[15px] font-semibold text-ink-300">
          {title}
        </h3>
      </div>
      {children}
    </div>
  );
}
