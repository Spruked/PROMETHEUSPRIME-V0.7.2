
Seed Vault Monitor
Tracks frequency of each a priori axiom used during CALI decision cycles.
"""

from typing import Dict
from collections import defaultdict

class SeedVaultMonitor:
    def __init__(self):
        self.usage_counts: Dict[str, int] = defaultdict(int)

    def log_axiom_use(self, axiom_id: str):
        self.usage_counts[axiom_id] += 1

    def get_usage_summary(self) -> Dict[str, int]:
        return dict(self.usage_counts)

    def get_top_used(self, top_n=5):
        return sorted(self.usage_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def get_unused(self, all_axioms: list):
        return [a for a in all_axioms if a not in self.usage_counts]