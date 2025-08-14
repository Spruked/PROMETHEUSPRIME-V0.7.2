"""
Echo Empirical Vault
Stores sensory- and experience-based evaluations from the EchoStack.
"""

from typing import Dict, List

class EchoEmpiricalVault:
    def __init__(self):
        self.memory: Dict[str, List[str]] = {
            "absolute": [],
            "conditional": [],
            "inconclusive": []
        }

    def store_observation(self, content: str, category: str):
        if category not in self.memory:
            raise ValueError("Invalid category")
        self.memory[category].append(content)

    def retrieve(self, category: str) -> List[str]:
        return self.memory.get(category, [])

    def summary(self) -> Dict[str, int]:
        return {k: len(v) for k, v in self.memory.items()}
