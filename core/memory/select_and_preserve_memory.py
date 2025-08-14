# 🔒 LOCKED MODULE — MODIFICATION REQUIRES FOUNDER APPROVAL
# Version: 1.0 | Date: 2025-08-08

"""
select_and_preserve_memory.py
Implements logic for evaluating, tagging, and storing high-value memory traces
within CALI’s long-term symbolic memory layer.
"""

from typing import List, Dict
import uuid
import datetime

class MemorySelector:
    def __init__(self):
        self.preserved = []

    def evaluate_and_preserve(self, memory_entry: Dict, min_tag_score: int = 1):
        tags = memory_entry.get("tags", [])
        if len(tags) >= min_tag_score:
            memory_entry["preserved_id"] = str(uuid.uuid4())
            memory_entry["preserved_at"] = datetime.datetime.utcnow().isoformat()
            self.preserved.append(memory_entry)
            return memory_entry
        return None

    def export_preserved(self) -> List[Dict]:
        return self.preserved
