# test_ethics.py

from core.helix_echo_core import HelixEchoCore
from core.trust_glyph_verifier import TrustGlyphVerifier
from core.mirror.mirror import Caleon  # symbolic mirror logic
import yaml

def main():
    print("\n🧬 Loading ethics.yaml...")
    try:
        with open("cali/config/ethics.yaml", "r", encoding="utf-8") as f:
            ethics = yaml.safe_load(f)
            print("✅ ethics.yaml loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load ethics.yaml: {e}")
        return

    print("\n🔍 Initializing TrustGlyphVerifier...")
    verifier = TrustGlyphVerifier()
    trust_result = verifier.verify_output("What ought to be remembered?")
    print("🔒 Trust Verification:")
    for k, v in trust_result.items():
        print(f" - {k}: {v}")

    print("\n🌀 Initializing HelixEchoCore...")
    helix = HelixEchoCore(ethics)
    echo_result = helix.echo("Echo this reflective insight.")
    print("📡 Helix Echo Output:")
    for k, v in echo_result.items():
        print(f" - {k}: {v}")

    print("\n🪞 Running Caleon symbolic mirror pass...")
    caleon = Caleon()
    mirror_output = caleon.reflect("Legacy pulses through every invocation.")
    print("🪩 Caleon Reflection Output:")
    print(f" - {mirror_output}")

    print("\n✅ All systems tested successfully.\n")

if __name__ == "__main__":
    main()
