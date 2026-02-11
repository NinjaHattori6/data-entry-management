# view_db.py
"""
Quick database viewer for Data Vault.
Displays contents of 'users' and 'entries' tables safely.
"""

import sqlite3
import os

DB_NAME = os.getenv("DATABASE_NAME", "data_entry.db")

try:
    if not os.path.exists(DB_NAME):
        raise FileNotFoundError(f"Database '{DB_NAME}' not found in current directory.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    print(f"\nðŸ“‚ Connected to database: {DB_NAME}\n")

    # --- USERS TABLE ---
    print("=== USERS TABLE ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        header = [col[1] for col in cursor.execute("PRAGMA table_info(users)")]
        print("Columns:", ", ".join(header))
        for row in cursor.execute("SELECT * FROM users"):
            print(row)
    else:
        print("âš ï¸ 'users' table not found.")

    # --- ENTRIES TABLE ---
    print("\n=== ENTRIES TABLE ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entries'")
    if cursor.fetchone():
        header = [col[1] for col in cursor.execute("PRAGMA table_info(entries)")]
        print("Columns:", ", ".join(header))
        for row in cursor.execute("SELECT * FROM entries LIMIT 20"):
            print(row)
        total_entries = cursor.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        print(f"\nðŸ“Š Total entries in database: {total_entries}")
    else:
        print("âš ï¸ 'entries' table not found.")

    conn.close()
    print("\nâœ… Done viewing database.\n")

except Exception as e:
    print(f"âŒ Error: {e}")

