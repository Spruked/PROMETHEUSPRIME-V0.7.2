import { useState } from "react";

export default function HelixEcho() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    const res = await fetch("/api/reflect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input }),
    });
    const data = await res.json();
    setResponse(data.response);
    setLoading(false);
  };

  return (
    <div className="p-4">
      <h2 className="text-xl mb-2">🧠 Talk to CALI (Mistral)</h2>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className="w-full p-2 border rounded bg-black text-green-400"
        rows={4}
        placeholder="What would you like to say?"
      />
      <button
        onClick={handleSubmit}
        className="mt-2 px-4 py-2 bg-green-600 text-white rounded"
        disabled={loading}
      >
        {loading ? "Thinking..." : "Reflect"}
      </button>

      {response && (
        <div className="mt-4 p-4 bg-gray-900 rounded text-green-300 whitespace-pre-wrap border border-green-600">
          <strong>Response:</strong>
          <div>{response}</div>
        </div>
      )}
    </div>
  );
}
