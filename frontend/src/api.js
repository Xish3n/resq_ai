const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function handleResponse(res) {
  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {
      /* ignore parse errors */
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function analyzeEmergency(description) {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description }),
  });
  return handleResponse(res);
}

export async function fetchScenarios() {
  const res = await fetch(`${API_BASE}/api/scenarios`);
  return handleResponse(res);
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  return handleResponse(res);
}
