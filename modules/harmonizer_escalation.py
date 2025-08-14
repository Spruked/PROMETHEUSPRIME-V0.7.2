"""
Harmonizer Escalation
Handles unresolved conflicts in verdicts. Retries logic loops with increasing tolerance.
Escalates to founder if resolution fails after 3 cycles.
"""

from modules.gyroscopic_harmonizer import GyroscopicHarmonizer

class HarmonizerEscalation:
    def __init__(self):
        self.harmonizer = GyroscopicHarmonizer()
        self.max_cycles = 3

    def escalate(self, case_id: str, helix_func, echo_func):
        """
        Attempts resolution by retrying helix and echo up to 3 times with escalating leniency.
        If no consensus, returns founder override flag.
        """
        for cycle in range(1, self.max_cycles + 1):
            helix = helix_func(case_id, cycle)
            echo = echo_func(case_id, cycle)
            result = self.harmonizer.harmonize(case_id, helix, echo)

            if result["consensus"]:
                return {**result, "cycles_used": cycle, "escalated": False}

        return {
            "final_verdict": "founder_intervention_required",
            "cycles_used": self.max_cycles,
            "escalated": True
        }
