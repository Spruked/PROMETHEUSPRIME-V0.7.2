from double_helix_core import PrometheusCodex
class CodexBridge:
    def __init__(self, codex):
        self.codex = codex

    def inquire_truth(self, topic):
        result = self.codex.query(topic)
        print(f"Truth Inquiry [{topic}]: {result}")

    def pulse_resonance(self):
        print("[Bridge] Resonance pulse transmitted.")

    def harmonic_sync(self, signal):
        print(f"[Bridge] Harmonic sync initiated with signal: {signal}")
