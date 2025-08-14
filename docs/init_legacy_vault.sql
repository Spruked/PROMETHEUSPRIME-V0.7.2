-- Run this SQL to create the legacy_vault table for testing
CREATE TABLE IF NOT EXISTS legacy_vault (
    title TEXT,
    description TEXT,
    triggers TEXT,
    delivery TEXT,
    unlock TEXT,
    is_active INTEGER,
    created_at TEXT,
    category TEXT
);
