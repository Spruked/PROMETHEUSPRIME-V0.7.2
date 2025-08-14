import React, { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";

export default function CaliSpeechSocket() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    // Connect to backend Socket.IO
    const socket = io("http://localhost:5000");
    socketRef.current = socket;

    socket.on("connect", () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));

    socket.on("cali_response", (data) => {
      setResponse(data.response);
      setLoading(false);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const handleSend = () => {
    if (!input.trim()) return;
    setLoading(true);
    setResponse("");
    socketRef.current.emit("user_speech_input", { input });
  };

  return (
    <div className="p-4">
      <h2 className="text-xl mb-2">🎤 Talk to CALI (WebSocket)</h2>
      <div style={{ marginBottom: 8 }}>
        <span style={{ color: connected ? '#22c55e' : '#f87171' }}>
          {connected ? "🟢 Connected" : "🔴 Disconnected"}
        </span>
      </div>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className="w-full p-2 border rounded bg-black text-green-400"
        rows={3}
        placeholder="Say something to CALI..."
        disabled={loading}
      />
      <button
        onClick={handleSend}
        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
        disabled={loading || !input.trim() || !connected}
      >
        {loading ? "Listening..." : "Send"}
      </button>
      {response && (
        <div className="mt-4 p-4 bg-gray-900 rounded text-green-300 whitespace-pre-wrap border border-blue-600">
          <strong>Response:</strong>
          <div>{response}</div>
        </div>
      )}
    </div>
  );
}
