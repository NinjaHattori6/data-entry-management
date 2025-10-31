import sqlite3

DB_NAME = "C:/Users/Warekar's/PycharmProjects/Data_entry_app/data_entry.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Check if 'is_admin' column exists
cur.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cur.fetchall()]

if 'is_admin' not in columns:
    cur.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    conn.commit()
    print("✅ Added 'is_admin' column to users table.")
else:
    print("ℹ️ Column 'is_admin' already exists — no changes made.")

conn.close()
