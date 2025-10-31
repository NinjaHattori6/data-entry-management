import sqlite3

DB_NAME = "C:/Users/Warekar's/PycharmProjects/Data_entry_app/data_entry.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("SELECT id, username FROM users")
users = cur.fetchall()

for uid, uname in users:
    cur.execute(
        "UPDATE entries SET user_id = ? WHERE username = ? AND (user_id IS NULL OR user_id = '')",
        (uid, uname)
    )
    print(f"Updated entries for {uname} → user_id = {uid}")

conn.commit()
conn.close()
print("✅ All entries updated successfully.")
