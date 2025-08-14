-- Legacy Vault Schema
CREATE TABLE IF NOT EXISTS legacy_vault (
    vault_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);