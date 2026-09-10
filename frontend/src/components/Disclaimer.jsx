import React from "react";

export default function Disclaimer({ text }) {
  return (
    <div className="flex gap-3 rounded-lg border border-signal-amber/30 bg-signal-amber/[0.06] px-5 py-4">
      <svg
        viewBox="0 0 24 24"
        fill="none"
        className="mt-0.5 h-5 w-5 shrink-0 text-signal-amber"
      >
        <path
          d="M12 3 2 20h20L12 3Z"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
        <path d="M12 10v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <circle cx="12" cy="17" r="0.9" fill="currentColor" />
      </svg>
      <p className="text-[13px] leading-relaxed text-ink-300">{text}</p>
    </div>
  );
}
