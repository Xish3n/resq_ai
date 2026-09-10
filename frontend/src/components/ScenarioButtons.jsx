import React from "react";

const SCENARIO_META = {
  flood: { label: "Flood", icon: "〜" },
  earthquake: { label: "Earthquake", icon: "≋" },
  fire: { label: "Fire", icon: "▲" },
  medical: { label: "Medical", icon: "+" },
};

export default function ScenarioButtons({ scenarios, onSelect, disabled, activeKey }) {
  const keys = Object.keys(SCENARIO_META).filter((k) => scenarios && scenarios[k]);

  return (
    <div className="flex flex-wrap gap-2">
      {keys.map((key) => {
        const meta = SCENARIO_META[key];
        const isActive = activeKey === key;
        return (
          <button
            key={key}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(key, scenarios[key])}
            className={`flex items-center gap-2 rounded-md border px-3.5 py-2 text-sm font-medium transition-colors
              disabled:cursor-not-allowed disabled:opacity-40
              ${
                isActive
                  ? "border-signal-cyan/50 bg-signal-cyan/10 text-signal-cyan"
                  : "border-base-600 bg-base-800 text-ink-300 hover:border-base-500 hover:text-ink-100"
              }`}
          >
            <span className="font-mono text-ink-700">{meta.icon}</span>
            {meta.label} scenario
          </button>
        );
      })}
    </div>
  );
}
