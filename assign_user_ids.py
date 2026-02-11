# assign_user_ids.py
"""
Safe script to populate entries.user_id from users table.
Creates DB backup before modifying data.
Only runs if entries table has a 'username' column.
"""

import sqlite3
import shutil
import os
from datetime import datetime

DB_NAME = os.getenv("DATABASE_NAME", "data_entry.db")
BACKUP = f"{DB_NAME}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"

def backup_db():
    try:
        shutil.copy2(DB_NAME, BACKUP)
        print(f"âœ… Backup created at: {BACKUP}")
    except Exception as e:
        print(f"âš ï¸ Backup failed: {e}")
        raise

def table_has_column(conn, table, column):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return column in [r[1] for r in cur.fetchall()]

def main():
    if not os.path.exists(DB_NAME):
        print(f"âŒ Database '{DB_NAME}' not found. Aborting.")
        return

    backup_db()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if not table_has_column(conn, "entries", "username"):
        print("âš ï¸ 'entries.username' column not found. Nothing to update.")
        conn.close()
        return

    cur.execute("SELECT id, username FROM users")
    mapping = {u[1].lower(): u[0] for u in cur.fetchall()}

    updated = 0
    for uname, uid in mapping.items():
        cur.execute(
            "UPDATE entries SET user_id = ? WHERE LOWER(username) = ? AND (user_id IS NULL OR user_id = 0)",
            (uid, uname)
        )
        updated += cur.rowcount

    conn.commit()
    conn.close()
    print(f"âœ… Updated {updated} entries successfully.")

if __name__ == "__main__":
    main()

