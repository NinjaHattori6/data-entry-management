"""
admin_tools.py
----------------------------------------
Admin Management Utility for Data Vault

Functions:
  1ï¸âƒ£ make_admin(email)     â†’ Promote user to admin
  2ï¸âƒ£ list_admins()         â†’ List all current admins
  3ï¸âƒ£ remove_admin(email)   â†’ Revoke admin rights from a user

Usage:
  Run this file in your terminal using:
      python admin_tools.py
----------------------------------------
"""

import sqlite3
import os

DB_NAME = "data_entry.db"  # Must match your app.py file

# --------------------------
# Utility Functions
# --------------------------
def connect_db():
    if not os.path.exists(DB_NAME):
        print(f"âŒ Database '{DB_NAME}' not found in this directory.")
        return None
    return sqlite3.connect(DB_NAME)

# --------------------------
# 1ï¸âƒ£ Promote a User to Admin
# --------------------------
def make_admin(email):
    conn = connect_db()
    if not conn:
        return
    cur = conn.cursor()

    cur.execute("SELECT id, username, is_admin FROM users WHERE email = ?", (email,))
    user = cur.fetchone()

    if not user:
        print(f"âš ï¸ No user found with email: {email}")
    elif user[2] == 1:
        print(f"âœ… '{email}' is already an admin.")
    else:
        cur.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
        conn.commit()
        print(f"ðŸ‘‘ '{email}' has been promoted to admin successfully!")

    conn.close()

# --------------------------
# 2ï¸âƒ£ List All Admins
# --------------------------
def list_admins():
    conn = connect_db()
    if not conn:
        return
    cur = conn.cursor()

    cur.execute("SELECT username, email FROM users WHERE is_admin = 1")
    admins = cur.fetchall()

    if not admins:
        print("âš ï¸ No admins found in the system.")
    else:
        print("\nðŸ§‘â€ðŸ’¼ Current Admins:")
        for idx, a in enumerate(admins, 1):
            print(f"  {idx}. {a[0]} ({a[1]})")

    conn.close()

# --------------------------
# 3ï¸âƒ£ Remove Admin Rights
# --------------------------
def remove_admin(email):
    conn = connect_db()
    if not conn:
        return
    cur = conn.cursor()

    cur.execute("SELECT id, username, is_admin FROM users WHERE email = ?", (email,))
    user = cur.fetchone()

    if not user:
        print(f"âš ï¸ No user found with email: {email}")
    elif user[2] == 0:
        print(f"â„¹ï¸ '{email}' is not an admin.")
    else:
        cur.execute("UPDATE users SET is_admin = 0 WHERE email = ?", (email,))
        conn.commit()
        print(f"ðŸš« '{email}' admin privileges removed.")

    conn.close()

# --------------------------
# 4ï¸âƒ£ Interactive Menu
# --------------------------
def main():
    print("\nðŸ› ï¸ Admin Management Tool")
    print("=" * 35)
    print("1ï¸âƒ£  Promote user to admin")
    print("2ï¸âƒ£  List all admins")
    print("3ï¸âƒ£  Remove admin privileges")
    print("4ï¸âƒ£  Exit")
    print("=" * 35)

    choice = input("Enter your choice (1-4): ").strip()

    if choice == "1":
        email = input("Enter user email to promote: ").strip()
        make_admin(email)
    elif choice == "2":
        list_admins()
    elif choice == "3":
        email = input("Enter admin email to remove: ").strip()
        remove_admin(email)
    elif choice == "4":
        print("ðŸ‘‹ Exiting Admin Tool. Goodbye!")
        return
    else:
        print("âŒ Invalid choice. Please try again.")

    print("\n----------------------------------------")
    input("Press Enter to continue...")
    main()  # Loop again

if __name__ == "__main__":
    main()

