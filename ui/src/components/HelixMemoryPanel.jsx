import React, { useEffect, useState } from "react";

const HelixMemoryPanel = () => {
  const [memory, setMemory] = useState([]);
  const [reflection, setReflection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMemory = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("/helix/memory");
        if (!res.ok) throw new Error("Failed to fetch memory");
        const data = await res.json();
        setMemory(data.epigenetic_memory || []);
        setReflection(data.last_reflection || null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchMemory();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h2>Helix Epigenetic Memory</h2>
      {loading && <div>Loading...</div>}
      {error && <div style={{ color: "red" }}>Error: {error}</div>}
      {!loading && !error && (
        <>
          <div style={{ maxHeight: 300, overflowY: "auto", border: "1px solid #ccc", borderRadius: 8, padding: 12, background: "#fafbfc" }}>
            {memory.length === 0 ? (
              <div>No memory entries yet.</div>
            ) : (
              <ul style={{ listStyle: "none", padding: 0 }}>
                {memory.map((entry, idx) => (
                  <li key={idx} style={{ marginBottom: 12, borderBottom: "1px solid #eee", paddingBottom: 8 }}>
                    <div><b>Type:</b> {entry.type || "?"}</div>
                    <div><b>Input:</b> {entry.input || JSON.stringify(entry)}</div>
                    <div><b>Response:</b> {entry.response || ""}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <h3 style={{ marginTop: 24 }}>Last Reflection</h3>
          <div style={{ minHeight: 40, background: "#f5f5f5", borderRadius: 6, padding: 10 }}>
            {reflection ? reflection : <span style={{ color: "#888" }}>No reflection yet.</span>}
          </div>
        </>
      )}
    </div>
  );
};

export default HelixMemoryPanel;
