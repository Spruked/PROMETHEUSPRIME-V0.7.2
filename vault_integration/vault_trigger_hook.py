import sqlite3
import time
import json
from ai_module.metadata_generator import generate_metadata
from ipfs_uploader.ipfs_upload import upload_to_ipfs
from minting_engine.mint_nft import mint_nft

DB_PATH = "prometheus_vault.db"
TRIGGER_TAG = "auto_mint"

def check_new_entries(last_seen_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, * FROM legacy_vault WHERE rowid > ? ORDER BY rowid ASC", (last_seen_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def process_entry(row):
    vault_id, title, description, triggers, delivery, unlock, is_active, created_at, category = row[1:]
    if TRIGGER_TAG in (triggers or ""):
        metadata_json = generate_metadata(title, description, "Prometheus Vault", [category, "vault-entry"])
        cid_link = upload_to_ipfs(metadata_json)
        tx_receipt = mint_nft(cid_link)
        print(f"✅ Auto-minted NFT for vault entry '{title}' — TX: {tx_receipt['transactionHash']}")
    else:
        print(f"⏩ Skipping '{title}' (no trigger tag)")

def monitor_vault():
    print("🔍 Monitoring Prometheus Vault for new entries...")
    last_seen_id = 0
    while True:
        try:
            new_rows = check_new_entries(last_seen_id)
            for row in new_rows:
                process_entry(row)
                last_seen_id = row[0]
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(5)

if __name__ == "__main__":
    monitor_vault()