import React from "react";

export default function Header({ liveMode }) {
  return (
    <header className="border-b border-base-600 bg-base-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-signal-amber/15 border border-signal-amber/40">
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 text-signal-amber">
              <path
                d="M12 2 3 6.5V12c0 5.2 3.6 9.6 9 11 5.4-1.4 9-5.8 9-11V6.5L12 2Z"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinejoin="round"
              />
              <path d="M12 8v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              <circle cx="12" cy="16" r="1" fill="currentColor" />
            </svg>
          </div>
          <div>
            <p className="text-[15px] font-bold leading-none tracking-tight">
              ResQ<span className="text-signal-amber">-AI</span>
            </p>
            <p className="text-xs text-ink-500 leading-none mt-1">
              Emergency Decision Support
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-full border border-base-600 bg-base-800 px-3 py-1.5 text-xs font-mono">
          <span
            className={`h-2 w-2 rounded-full ${
              liveMode === null ? "bg-ink-700" : liveMode ? "bg-risk-low pulse-dot" : "bg-signal-amber"
            }`}
          />
          <span className="text-ink-300">
            {liveMode === null ? "connecting" : liveMode ? "live LLM mode" : "offline demo mode"}
          </span>
        </div>
      </div>
    </header>
  );
}
