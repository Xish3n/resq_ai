import React from "react";
import ScenarioButtons from "./ScenarioButtons.jsx";

export default function InputPanel({
  description,
  setDescription,
  onAnalyze,
  loading,
  scenarios,
  onSelectScenario,
  activeScenario,
  error,
}) {
  return (
    <div className="rounded-xl border border-base-600 bg-base-800/80 p-6 sm:p-8 shadow-panel">
      <div className="max-w-2xl">
        <h1 className="text-2xl sm:text-[28px] font-bold tracking-tight text-ink-100">
          Describe the emergency
        </h1>
        <p className="mt-2 text-[15px] leading-relaxed text-ink-500">
          Enter a situation in plain language. ResQ-AI's agent pipeline will extract the key
          facts, assess risk, pull relevant emergency guidelines, and draft a reviewed
          response plan for a human coordinator.
        </p>
      </div>

      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="e.g. Heavy flooding has affected an area. Around 100 people are stranded and 5 people need medical assistance."
        rows={5}
        disabled={loading}
        className="mt-5 w-full resize-none rounded-lg border border-base-600 bg-base-900 px-4 py-3.5 text-[15px]
          text-ink-100 placeholder:text-ink-700 outline-none transition-colors
          focus:border-signal-cyan/50 focus:ring-1 focus:ring-signal-cyan/30 disabled:opacity-50"
      />

      {error && (
        <p className="mt-2 text-sm text-risk-critical">{error}</p>
      )}

      <div className="mt-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <ScenarioButtons
          scenarios={scenarios}
          onSelect={onSelectScenario}
          disabled={loading}
          activeKey={activeScenario}
        />

        <button
          type="button"
          onClick={onAnalyze}
          disabled={loading || description.trim().length < 5}
          className="flex items-center justify-center gap-2 rounded-md bg-signal-amber px-6 py-2.5 text-sm font-semibold
            text-base-950 transition-transform hover:brightness-110 active:scale-[0.98]
            disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:brightness-100 whitespace-nowrap"
        >
          {loading ? (
            <>
              <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-base-950/30 border-t-base-950" />
              Analyzing…
            </>
          ) : (
            "Analyze emergency"
          )}
        </button>
      </div>
    </div>
  );
}
