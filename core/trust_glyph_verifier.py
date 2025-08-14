# core/trust_glyph_verifier.py

import yaml

class TrustGlyphVerifier:
    """
    TrustGlyphVerifier:
    Validates symbolic ethical coherence and legacy-based trust before final output.
    """

    def __init__(self, config_path="cali/config/ethics.yaml"):
        self.config_path = config_path
        self.ethics = self._load_ethics()

    def _load_ethics(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load ethics.yaml: {e}")
            return {}

    def verify_output(self, data):
        return {
            "trust_signature_valid": self._check_trust_signature(),
            "resonance_pass": self._emotional_resonance_pass(data),
            "legacy_pulse_ack": self._legacy_pulse_check(data)
        }

    def _check_trust_signature(self):
        glyph = self.ethics.get("identity", {}).get("trust_glyph_signature")
        return glyph is not None and glyph.startswith("Σ")

    def _emotional_resonance_pass(self, data):
        disallowed = self.ethics.get("emotional_filters", {}).get("disallowed_tones", [])
        return not any(tone in data.lower() for tone in disallowed)

    def _legacy_pulse_check(self, data):
        pulse_config = self.ethics.get("invocation_protocol", {}).get("legacy_pulse_check", {})
        return pulse_config.get("enabled", False) and "remember" in data.lower()
