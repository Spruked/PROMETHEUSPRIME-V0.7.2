
Gyroscopic Harmonizer
Balances outputs from DoubleHelix and EchoStack.
Uses resolution logic and optionally triggers escalation.
"""

from vaults.resolution_vault import ResolutionVault

class GyroscopicHarmonizer:
    def __init__(self):
        self.vault = ResolutionVault()

    def harmonize(self, case_id: str, helix_result: dict, echo_result: dict):
        """
        Takes structured verdicts from Helix and EchoStack.
        Returns final category and stores result.
        """

        h_cat = helix_result.get("category")
        e_cat = echo_result.get("category")

        # Simple alignment
        if h_cat == e_cat:
            self.vault.store_resolution(case_id, h_cat, "harmonizer")
            return {"final_verdict": h_cat, "consensus": True}

        # Conflict handling
        priority = self.resolve_priority(h_cat, e_cat)
        self.vault.store_resolution(case_id, priority, "harmonizer (disagreement)")
        return {"final_verdict": priority, "consensus": False}

    def resolve_priority(self, h_cat: str, e_cat: str) -> str:
        """
        Resolves disagreement between modules.
        Favors most cautious interpretation.
        """
        order = ["inconclusive", "conditional", "absolute"]
        ranked = sorted([h_cat, e_cat], key=lambda x: order.index(x))
        return ranked[0]  # Favor lower certainty if conflict