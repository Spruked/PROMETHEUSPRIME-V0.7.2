# build_db.py

import sqlite3

def init_db():
    with open("vault_schema.sql", "r") as f:
        schema = f.read()

    conn = sqlite3.connect("prometheus_vault.db")
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("Database created and schema loaded successfully.")
