"""
Resolution Vault
Stores final verdicts categorized by certainty for traceable ethics history.
"""

from typing import Dict, List

class ResolutionVault:
    def __init__(self):
        self.entries: Dict[str, List[str]] = {
            "absolute": [],
            "conditional": [],
            "inconclusive": []
        }

    def store_resolution(self, verdict_id: str, category: str, source: str):
        if category not in self.entries:
            raise ValueError("Invalid category")
        entry = f"{verdict_id} from {source}"
        self.entries[category].append(entry)

    def get_category(self, category: str) -> List[str]:
        return self.entries.get(category, [])

    def summarize(self) -> Dict[str, int]:
        return {k: len(v) for k, v in self.entries.items()}
