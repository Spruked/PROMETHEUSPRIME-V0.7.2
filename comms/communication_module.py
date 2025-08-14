"""
Communication Module (Backend)
Handles voice input/output orchestration for CALI.
Integrates speech-to-text and text-to-speech endpoints.
"""

from typing import Dict

class CommunicationModule:
    def __init__(self):
        self.history = []

    def receive_voice_input(self, text: str) -> Dict:
        self.history.append({"input": text})
        return {"status": "received", "text": text}

    def synthesize_voice_output(self, response: str) -> Dict:
        self.history.append({"output": response})
        return {"status": "spoken", "text": response}

    def get_history(self):
        return self.history