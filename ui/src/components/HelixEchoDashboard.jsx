import React, { useState, useEffect } from "react";
import "./HelixEchoDashboard.css";

const api = (path, opts = {}) =>
  fetch(`http://localhost:5000${path}`, opts).then(r => r.json());

export default function HelixEchoDashboard() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    const data = await api("/helix/status");
    setStatus(data);
  };

  const handleProcess = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setResponse(null);
    try {
      const res = await api("/helix/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input }),
      });
      setResponse(res.helix_response || res.error);
      fetchStatus();
    } catch (e) {
      setResponse("Error connecting to Helix Echo Core.");
    }
    setLoading(false);
  };

  return (
    <div className="helix-echo-dashboard">
      <h2>🔥 Helix Echo Core Dashboard</h2>
      <div className="helix-echo-controls">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type a thought or question for Helix..."
          rows={3}
          disabled={loading}
        />
        <button onClick={handleProcess} disabled={loading || !input.trim()}>
          {loading ? "Processing..." : "Process"}
        </button>
      </div>
      {response && (
        <div className="helix-echo-response">
          <strong>Response:</strong>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
      {status && status.available && (
        <div className="helix-echo-status">
          <h3>System Status</h3>
          <pre>{JSON.stringify(status.status, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
