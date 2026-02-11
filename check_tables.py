import sqlite3

DB = "data_entry.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

print("\n--- USERS TABLE ---")
cur.execute("PRAGMA table_info(users);")
for row in cur.fetchall():
    print(row)

print("\n--- ENTRIES TABLE ---")
cur.execute("PRAGMA table_info(entries);")
for row in cur.fetchall():
    print(row)

conn.close()

