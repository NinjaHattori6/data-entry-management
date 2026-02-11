# fix_db_admin_column.py
"""
Adds 'is_admin' column to users table if missing.
Creates a database backup before modifying schema.
"""

import sqlite3
import os
import shutil
from datetime import datetime

DB_NAME = os.getenv("DATABASE_NAME", "data_entry.db")
BACKUP = f"{DB_NAME}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"

def backup_db():
    try:
        shutil.copy2(DB_NAME, BACKUP)
        print(f"âœ… Backup created at: {BACKUP}")
    except Exception as e:
        print(f"âš ï¸ Backup failed: {e}")

def main():
    if not os.path.exists(DB_NAME):
        print(f"âŒ Database '{DB_NAME}' not found. Aborting.")
        return

    backup_db()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cur.fetchall()]

    if 'is_admin' not in columns:
        try:
            cur.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            conn.commit()
            print("âœ… Added 'is_admin' column to users table.")
            # Optional: promote first user to admin automatically
            cur.execute("UPDATE users SET is_admin = 1 WHERE id = 1")
            conn.commit()
            print("ðŸ‘‘ Promoted first user (ID=1) to admin.")
        except Exception as e:
            print(f"âŒ Failed to add column: {e}")
    else:
        print("â„¹ï¸ Column 'is_admin' already exists â€” no changes needed.")

    conn.close()
    print("âœ… Database check complete.")

if __name__ == "__main__":
    main()

