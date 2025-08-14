import React, { useEffect, useState } from "react";
import io from "socket.io-client";
import yaml from "js-yaml";

async function fetchSignalMatrix() {
  const res = await fetch("/nucleus/signal_voice_matrix.yaml");
  const text = await res.text();
  return yaml.load(text).signal_voice_matrix;
}

const socket = io("http://localhost:5050");

export default function SignalStateNode() {
  const [currentState, setCurrentState] = useState("Dormant");
  const [matrix, setMatrix] = useState([]);

  useEffect(() => {
    fetchSignalMatrix().then(setMatrix);
    socket.on("state_update", (data) => {
      setCurrentState(data.state);
    });
    return () => socket.off("state_update");
  }, []);

  const entry = matrix.find((item) => item.state === currentState);

  return (
    <div className={`state-node ${currentState.toLowerCase().replace(/\s+/g, "-")}`}>
      <span className="tooltip">
        {entry
          ? `${entry.biological_metaphor} (${entry.functionality})`
          : "Unknown State"}
      </span>
      <span className="state-label">{currentState}</span>
      <span className="classification-tag">
        {entry?.classification ?? "Unclassified"}
      </span>
    </div>
  );
}
