# core/helix_echo_core.py

class HelixEchoCore:
    """
    HelixEchoCore:
    Core symbolic echo harmonizer that processes data across multiple layers—
    memory, ethics, trust alignment, and interpretive drift awareness.
    """

    def __init__(self, ethics=None):
        self.ethics = ethics or {}
        self.echo_log = []

    def echo(self, input_data):
        """
        Process an input signal symbolically and apply Sixth Layer resonance checks.
        """
        response = {
            "input": input_data,
            "resonance": self._apply_resonance_filter(input_data),
            "trust_glyph_passed": self._trust_glyph_validation(input_data),
            "output": f"Reflective echo: '{input_data}'",
        }
        self.echo_log.append(response)
        return response

    def _apply_resonance_filter(self, data):
        tones = self.ethics.get("emotional_filters", {}).get("prioritized_emotional_tones", [])
        disallowed = self.ethics.get("emotional_filters", {}).get("disallowed_tones", [])
        return {
            "priority_tones": tones,
            "disallowed_tones": disallowed,
            "passed": all(t not in data.lower() for t in disallowed)
        }

    def _trust_glyph_validation(self, data):
        glyph_required = self.ethics.get("identity", {}).get("trust_glyph_signature", None)
        legacy_mode = self.ethics.get("identity", {}).get("invocation_level", "")
        return glyph_required is not None and legacy_mode == "Sixth Layer"

    def last_echo(self):
        return self.echo_log[-1] if self.echo_log else None
