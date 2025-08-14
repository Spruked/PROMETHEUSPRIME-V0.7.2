import time

class MemoryStore:
    def __init__(self):
        self._store = {}
        self._id = 1

    def add_entry(self, text, emotion=None, context=None, tags=None, usage_score=1.0):
        entry = {
            "id": self._id,
            "text": text,
            "emotion": emotion,
            "context": context,
            "tags": tags,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "usage_score": usage_score
        }
        self._store[self._id] = entry
        self._id += 1
        return entry["id"]

    def get_entry(self, entry_id):
        entry = self._store.get(entry_id)
        if entry:
            return [entry[k] for k in ["id", "text", "emotion", "context", "tags", "created_at", "usage_score"]]
        return None

    def search_text(self, q):
        return [
            [e[k] for k in ["id", "text", "emotion", "context", "tags", "created_at", "usage_score"]]
            for e in self._store.values() if q.lower() in (e["text"] or "").lower()
        ]

    def search_by_tag(self, tag):
        return [
            [e[k] for k in ["id", "text", "emotion", "context", "tags", "created_at", "usage_score"]]
            for e in self._store.values() if e["tags"] and tag in e["tags"]
        ]

    def search_recent(self, n):
        entries = list(self._store.values())
        entries.sort(key=lambda e: e["created_at"], reverse=True)
        return [
            [e[k] for k in ["id", "text", "emotion", "context", "tags", "created_at", "usage_score"]]
            for e in entries[:n]
        ]
