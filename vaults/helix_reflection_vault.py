"""
Helix Reflection Vault
Stores rational deductions from the Double Helix reasoning module.
"""

from typing import Dict, List

class HelixReflectionVault:
    def __init__(self):
        self.absolute: List[str] = []
        self.conditional: List[str] = []
        self.inconclusive: List[str] = []

    def log(self, content: str, certainty: str = "inconclusive"):
        if certainty == "absolute":
            self.absolute.append(content)
        elif certainty == "conditional":
            self.conditional.append(content)
        else:
            self.inconclusive.append(content)

    def export(self) -> Dict[str, List[str]]:
        return {
            "absolute": self.absolute,
            "conditional": self.conditional,
            "inconclusive": self.inconclusive,
        }
