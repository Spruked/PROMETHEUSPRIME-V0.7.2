# Added enter_hibernation for vault reflection and hibernation
from cali.vault.vaultkeeper import load_memory_vault
from whispering_archive import WhisperingArchive
from double_helix_core import PrometheusCodex
from codex_bridge import CodexBridge
def enter_hibernation(vault_id):
    try:
        vault = load_memory_vault(vault_id)
        if not vault:
            print(f"[WARN] No vault found with ID {vault_id}.")
            return

        codex = PrometheusCodex()
        bridge = CodexBridge(codex)
        archive = WhisperingArchive()

        print(f"[INFO] Reflecting on vault: {vault_id} with {len(vault['entries'])} entries...")

        bridge.inquire_truth("reflection")
        bridge.harmonic_sync("hibernation")

        archive.log(bridge.echo_log, actor="Cali.Hibernate")
        print("[OK] Vault reflection completed.")

    except Exception as e:
        print(f"[ERROR] Hibernation failed: {e}")
# PrometheusPrime/helix/consolidate.py
# Executes Prometheus Prime's HIBERNATION PHASE.
# Consolidates CodexBridge memory, secures vault, prepares for rest mode.

from whispering_archive import WhisperingArchive
from codex_bridge import CodexBridge
from double_helix_core import PrometheusCodex
from cali.vault.vaultkeeper import load_memory_vault, save_memory_vault
from cali.vault.reconciliation import reconcile_entries, save_reconciled_summary
from core.caleon_core import CaleonPrime
import uuid
from datetime import datetime

def consolidate_session(vault_id: str):
    print("🛌 Initiating hibernation phase...")

    # Initialize systems
    codex = PrometheusCodex()
    bridge = CodexBridge(codex)
    archive = WhisperingArchive()
    caleon = CaleonPrime()

    # Retrieve current vault data
    vault = load_memory_vault(vault_id)
    if not vault:
        print(f"⚠️ Vault {vault_id} not found. Exiting hibernation.")
        return

    # Reconcile memory
    entries = vault.get("entries", [])
    if not entries:
        print("⚠️ Vault is empty.")
        return

    reconciled = reconcile_entries(entries)
    summary = {
        "archive_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "synthesized_count": len(reconciled),
        "entries": reconciled[:10]
    }

    # Save summary to vault
    vault["reconciled"] = summary
    save_memory_vault(vault_id, vault)

    # Archive the result
    archive.log(reconciled, actor="CaleonPrime")
    print("📦 Hibernation complete. Vault secured.")

    return summary
