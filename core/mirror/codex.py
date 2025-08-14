class LocalCodex:
    def __init__(self, model="mistral", base_url=None):
        self.model = model
        self.base_url = base_url

    def query(self, text: str) -> str:
        # Placeholder logic
        return f"Codex({self.model}) received: {text}"
