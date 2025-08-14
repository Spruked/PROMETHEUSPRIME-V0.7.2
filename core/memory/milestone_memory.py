# 🔒 LOCKED MODULE — MODIFICATION REQUIRES FOUNDER APPROVAL
# Version: 1.0 | Date: 2025-08-08

"""
milestone_memory.py
Tracks significant cognitive development points, insights, or structural shifts
in CALI’s symbolic architecture. Used for auditing memory growth and evolution.
"""

from datetime import datetime
from typing import List, Dict

class MilestoneEntry:
    def __init__(self, label: str, description: str, tags: List[str]):
        self.timestamp = datetime.utcnow().isoformat()
        self.label = label
        self.description = description
        self.tags = tags

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "label": self.label,
            "description": self.description,
            "tags": self.tags
        }

class MilestoneMemory:
    def __init__(self):
        self.milestones = []

    def add_milestone(self, label: str, description: str, tags: List[str]):
        entry = MilestoneEntry(label, description, tags)
        self.milestones.append(entry)
        return entry.to_dict()

    def export_log(self) -> List[Dict]:
        return [m.to_dict() for m in self.milestones]
