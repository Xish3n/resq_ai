import React, { useEffect, useState } from "react";
import Header from "./components/Header.jsx";
import InputPanel from "./components/InputPanel.jsx";
import Dashboard from "./components/Dashboard.jsx";
import PipelineTrace from "./components/PipelineTrace.jsx";
import { analyzeEmergency, fetchScenarios, fetchHealth } from "./api.js";

export default function App() {
  const [description, setDescription] = useState("");
  const [scenarios, setScenarios] = useState(null);
  const [activeScenario, setActiveScenario] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [liveMode, setLiveMode] = useState(null);

  useEffect(() => {
    fetchScenarios()
      .then(setScenarios)
      .catch(() => setScenarios(null));

    fetchHealth()
      .then((h) => setLiveMode(h.llm_mode === "live"))
      .catch(() => setLiveMode(false));
  }, []);

  const handleSelectScenario = (key, text) => {
    setActiveScenario(key);
    setDescription(text);
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (description.trim().length < 5) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeEmergency(description);
      setResult(data);
    } catch (err) {
      setError(
        err.message ||
          "Something went wrong reaching the ResQ-AI backend. Confirm the API server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <Header liveMode={liveMode} />

      <main className="mx-auto max-w-6xl px-6 py-10">
        <InputPanel
          description={description}
          setDescription={(val) => {
            setDescription(val);
            setActiveScenario(null);
          }}
          onAnalyze={handleAnalyze}
          loading={loading}
          scenarios={scenarios}
          onSelectScenario={handleSelectScenario}
          activeScenario={activeScenario}
          error={error}
        />

        {loading && !result && (
          <div className="mt-8">
            <PipelineTrace modes={null} loading={true} />
          </div>
        )}

        <Dashboard result={result} />
      </main>

      <footer className="mx-auto max-w-6xl px-6 pb-10 pt-4">
        <p className="text-xs text-ink-700">
          ResQ-AI is a hackathon decision-support prototype. It does not contact emergency
          services or replace professional responders.
        </p>
      </footer>
    </div>
  );
}
