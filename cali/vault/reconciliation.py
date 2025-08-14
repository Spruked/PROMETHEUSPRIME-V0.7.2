# cali/vault/reconciliation.py

def reconcile_entries(entries):
    # Dummy logic for reconciliation
    reconciled = list({entry['id']: entry for entry in entries}.values())
    return reconciled

def save_reconciled_summary(summary, filepath="vault/reconciled_summary.json"):
    import json
    with open(filepath, "w") as f:
        json.dump(summary, f, indent=4)
