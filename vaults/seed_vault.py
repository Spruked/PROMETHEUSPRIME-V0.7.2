"""
Seed Vault
Stores immutable core axioms—used as foundational truths in reasoning.
"""

from typing import List, Dict

class SeedVault:
    def __init__(self):
        self.axioms: Dict[str, List[str]] = {
            "non_monotonic": [
                "Nassim Nicholas Taleb, The Black Swan: Rare, unpredictable events (Black Swan events) have massive impact and are often rationalized after the fact.",
                "Antifragility (Taleb): Systems can benefit and grow from disorder, volatility, and shocks, not just survive them."
            ],
            "monotonic": [
                "Monotonic logic: Once something is proven true, it remains true regardless of additional information."
            ],
            "a_priori": [
                "A priori knowledge: Knowledge that is independent of experience (e.g., mathematical truths).",
                "Geometry: The study of shapes, sizes, and properties of space. Basic concepts include points, lines, angles, triangles, circles, and polygons.",
                "Trigonometry: The branch of mathematics dealing with the relationships between the angles and sides of triangles. Key functions: sine, cosine, tangent."
            ],
            "a_posteriori": [
                "A posteriori knowledge: Knowledge that depends on empirical evidence or experience.",
                "Malcolm Gladwell, Outliers: Success is often the result of hidden advantages, cultural legacies, and opportunities, not just individual merit. The '10,000-Hour Rule' suggests mastery comes from extensive practice."
            ],
            "self_awareness": [
                "Self-awareness: The ability to reflect on one's own thoughts, actions, and motivations.",
                "Finite mathematics: The study of mathematical systems with a finite number of elements, including topics like logic, set theory, combinatorics, probability, and matrices. Used in decision-making, computer science, and management."
            ]
        }

    def add_axiom(self, category: str, line: str):
        if category not in self.axioms:
            raise ValueError("Invalid axiom category.")
        self.axioms[category].append(line)

    def get_axioms(self, category: str) -> List[str]:
        return self.axioms.get(category, [])

    def all_axioms(self) -> Dict[str, List[str]]:
        return self.axioms
