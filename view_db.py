import sqlite3

DB_NAME = "data_entry.db"

try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print(f"\n📂 Connected to database: {DB_NAME}\n")

    # --- View Users Table ---
    print("=== USERS TABLE ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        for row in cursor.execute("SELECT * FROM users"):
            print(row)
    else:
        print("⚠️  'users' table not found.")

    print("\n=== ENTRIES TABLE ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entries'")
    if cursor.fetchone():
        for row in cursor.execute("SELECT * FROM entries"):
            print(row)
    else:
        print("⚠️  'entries' table not found.")

    conn.close()
    print("\n✅ Done viewing database.\n")

except Exception as e:
    print(f"❌ Error: {e}")
