
class VaultNavigator:
    def __init__(self):
        self.vaults: Dict[str, List[Dict]] = {
            "resolution": [],
            "helix": [],
            "echo": [],
            "seed": []
        }

    def load_vault(self, vault_name: str, entries: List[Dict]):
        if vault_name not in self.vaults:
            self.vaults[vault_name] = []
        self.vaults[vault_name].extend(entries)

    def search(self, keyword: str) -> List[Dict]:
        results = []
        for entries in self.vaults.values():
            results.extend([e for e in entries if keyword.lower() in str(e).lower()])
        return results

    def export_all(self) -> Dict[str, List[Dict]]:
        return self.vaults

    def print_summary(self) -> Dict[str, int]:
        return {vault: len(entries) for vault, entries in self.vaults.items()}
