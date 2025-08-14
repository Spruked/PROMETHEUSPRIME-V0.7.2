import React, { useEffect, useState } from "react";

const VoiceInterface = () => {
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");

  const synth = window.speechSynthesis;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;

  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
    setResponse(text);
  };

  const startListening = () => {
    if (!recognition) return;
    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = (event: any) => {
      const result = event.results[0][0].transcript;
      setTranscript(result);
      // Simulated response:
      speak("I heard you say: " + result);
    };
  };

  return (
    <div>
      <h3>🎤 Voice Interface</h3>
      <button onClick={startListening}>Start Listening</button>
      <p><strong>Input:</strong> {transcript}</p>
      <p><strong>Response:</strong> {response}</p>
    </div>
  );
};

export default VoiceInterface;
