import sqlite3
import os
import shutil

DB_NAME = os.getenv("DATABASE_NAME", "data_entry.db")

def backup_db(db_name):
    backup_name = f"{db_name}.backup"
    shutil.copy(db_name, backup_name)
    print(f"âœ… Backup created: {backup_name}")

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    return column in cols

def verify_and_fix_db():
    if not os.path.exists(DB_NAME):
        print(f"âŒ Database '{DB_NAME}' not found.")
        return

    backup_db(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ---- USERS table ----
    try:
        if not column_exists(cursor, "users", "is_admin"):
            print("âš™ï¸ Adding 'is_admin' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;")
            print("âœ… Added 'is_admin' column.")
        else:
            print("âœ… 'is_admin' column already exists in users table.")
    except Exception as e:
        print(f"âŒ Error updating users table: {e}")

    # ---- ENTRIES table ----
    try:
        if not column_exists(cursor, "entries", "user_id"):
            print("âš™ï¸ Adding 'user_id' column to entries table...")
            cursor.execute("ALTER TABLE entries ADD COLUMN user_id INTEGER;")
            print("âœ… Added 'user_id' column.")
        else:
            print("âœ… 'user_id' column already exists in entries table.")
    except Exception as e:
        print(f"âŒ Error updating entries table: {e}")

    conn.commit()
    conn.close()
    print("ðŸŽ¯ Database verification complete.")

if __name__ == "__main__":
    verify_and_fix_db()

