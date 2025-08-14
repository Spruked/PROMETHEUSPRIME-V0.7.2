import React, { useState, useEffect } from "react";
import "./MemoryConsole.css";

const api = (path, opts = {}) =>
  fetch(`http://localhost:5000${path}`, opts).then(r => r.json());

export default function MemoryConsole() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchRecent();
  }, []);

  const fetchRecent = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api("/memory/recent?n=10");
      setRecent(data);
    } catch (e) {
      setError("Could not load recent memory.");
    }
    setLoading(false);
  };

  const handleSearch = async e => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await api(`/memory/search?q=${encodeURIComponent(query)}`);
      setResults(data);
    } catch (e) {
      setError("Search failed.");
    }
    setLoading(false);
  };

  const handleTagSearch = async tag => {
    setLoading(true);
    setError("");
    try {
      const data = await api(`/memory/tag/${encodeURIComponent(tag)}`);
      setResults(data);
    } catch (e) {
      setError("Tag search failed.");
    }
    setLoading(false);
  };

  return (
    <div className="memory-console">
      <h2>🧠 CALI Memory Console</h2>
      <form onSubmit={handleSearch} className="memory-search-form">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search memory by text..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          Search
        </button>
        <button type="button" onClick={fetchRecent} disabled={loading}>
          Recent
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      <div className="memory-results">
        {loading && <div className="loading">Loading...</div>}
        {!loading && results.length > 0 && (
          <div>
            <h3>Search Results</h3>
            <MemoryList entries={results} onTag={handleTagSearch} />
          </div>
        )}
        {!loading && results.length === 0 && recent.length > 0 && (
          <div>
            <h3>Recent Memory</h3>
            <MemoryList entries={recent} onTag={handleTagSearch} />
          </div>
        )}
      </div>
    </div>
  );
}

function MemoryList({ entries, onTag }) {
  if (!entries || entries.length === 0) return <div>No memory found.</div>;
  return (
    <ul className="memory-list">
      {entries.map(e => (
        <li key={e.id} className="memory-entry">
          <div className="memory-text">{e.text}</div>
          <div className="memory-meta">
            <span className="memory-emotion">{e.emotion}</span>
            <span className="memory-context">{e.context}</span>
            <span className="memory-date">{new Date(e.created_at).toLocaleString()}</span>
            {e.tags && e.tags.split && e.tags.split(",").filter(Boolean).map(tag => (
              <span
                key={tag}
                className="memory-tag"
                onClick={() => onTag(tag)}
                title="Search by tag"
              >
                #{tag}
              </span>
            ))}
          </div>
        </li>
      ))}
    </ul>
  );
}
