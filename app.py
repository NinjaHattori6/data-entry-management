# FINAL CLEAN APP.PY â€” FULLY COMPATIBLE WITH YOUR DB SCHEMA

import os
import time
import sqlite3
import random
from functools import wraps
from datetime import timedelta, datetime
from io import BytesIO

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ---------------------------------------------------------
# LOGGING + EMAIL SUPPORT
# ---------------------------------------------------------

import logging
import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------------------------------------------------
# LOAD CONFIG
# ---------------------------------------------------------

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_change_me")
DB_NAME = os.getenv("DATABASE_NAME", "data_entry.db")

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False

import secrets

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.get("_csrf_token")
        form_token = request.form.get("_csrf_token")
        if not token or token != form_token:
            abort(403)

def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(16)
    return session["_csrf_token"]

app.jinja_env.globals["csrf_token"] = generate_csrf_token


# ---------------------------------------------------------
# DATABASE HELPER
# ---------------------------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------
# AUTH DECORATORS
# ---------------------------------------------------------

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Admins only.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------
# OTP SYSTEM
# ---------------------------------------------------------

OTP_TTL = 300

def generate_and_store_otp(email):
    otp = random.randint(100000, 999999)
    session["otp"] = str(otp)
    session["otp_email"] = email
    session["otp_exp"] = time.time() + OTP_TTL
    return otp


def validate_otp(entered):
    otp = session.get("otp")
    exp = session.get("otp_exp")
    if not otp:
        return False, "No OTP found."
    if time.time() > exp:
        session.pop("otp", None)
        session.pop("otp_exp", None)
        return False, "OTP expired."
    if str(entered) != otp:
        return False, "Invalid OTP."
    session.pop("otp", None)
    session.pop("otp_exp", None)
    return True, "OTP correct."

def send_otp_email(receiver_email, otp):
    if not EMAIL_USER or not EMAIL_PASS:
        logging.error("Email credentials not configured.")
        return False

    try:
        msg = MIMEText(
            f"Your OTP for Data Vault password reset is: {otp}\n\nValid for 5 minutes."
        )
        msg["Subject"] = "Data Vault - OTP Verification"
        msg["From"] = EMAIL_USER
        msg["To"] = receiver_email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, receiver_email, msg.as_string())
        server.quit()

        logging.info(f"OTP sent to {receiver_email}")
        return True

    except Exception as e:
        logging.error(f"Email error: {e}")
        return False


# ---------------------------------------------------------
# INDEX
# ---------------------------------------------------------

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not username or not email or not password:
            flash("All fields required.", "warning")
            return redirect(url_for("register"))

        pwd_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)",
                (username, email, pwd_hash, 0)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Email already registered.", "danger")
            conn.close()
            return redirect(url_for("register"))

        conn.close()
        flash("Registered successfully! Log in now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password"], password):
            logging.warning(f"Failed login attempt: {email}")
            logging.info(f"User logged in: {email}")
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["email"] = user["email"]
        session["is_admin"] = bool(user["is_admin"])

        flash(f"Welcome, {user['username']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

@app.route("/logout")
def logout():
    logging.info(f"User logged out: {session.get('email')}")
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------
# FORGOT PASSWORD (OTP)
# ---------------------------------------------------------

@app.route("/forget", methods=["GET", "POST"])
def forget():
    if request.method == "POST":
        email = request.form["email"].strip().lower()

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if not user:
            flash("Email not found.", "danger")
            return redirect(url_for("forget"))

        otp = generate_and_store_otp(email)

        if send_otp_email(email, otp):
            flash("OTP sent to your registered email.", "info")
        else:
            flash("Failed to send OTP email. Contact admin.", "danger")
            return redirect(url_for("forget"))

        return redirect(url_for("otp"))

    return render_template("forget.html")


@app.route("/otp", methods=["GET", "POST"])
def otp():
    if request.method == "POST":
        entered = request.form["otp"]
        ok, msg = validate_otp(entered)

        if ok:
            session["reset_email"] = session.get("otp_email")
            flash("OTP verified.", "success")
            return redirect(url_for("reset_password"))

        flash(msg, "danger")
        return redirect(url_for("otp"))

    return render_template("otp.html")


@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    email = session.get("reset_email")
    if not email:
        flash("No OTP verification found.", "warning")
        return redirect(url_for("forget"))

    if request.method == "POST":
        new_pw = request.form["password"]
        hashed = generate_password_hash(new_pw)

        conn = get_db_connection()
        conn.execute("UPDATE users SET password=? WHERE email=?", (hashed, email))
        conn.commit()
        conn.close()

        session.pop("reset_email", None)
        flash("Password updated.", "success")
        return redirect(url_for("login"))

    return render_template("reset.html")


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()

    # 👑 ADMIN → see ALL entries + user name
    if session.get('is_admin'):
        entries = conn.execute("""
            SELECT 
                entries.id,
                entries.name,
                entries.gender,
                entries.amount,
                entries.date,
                users.username AS owner_name
            FROM entries
            JOIN users ON entries.user_id = users.id
            ORDER BY entries.id DESC
        """).fetchall()

    # 👤 NORMAL USER → see only own entries
    else:
        entries = conn.execute("""
            SELECT id, name, gender, amount, date
            FROM entries
            WHERE user_id = ?
            ORDER BY id DESC
        """, (session['user_id'],)).fetchall()

    # 📊 Stats
    total_entries = len(entries)
    total_amount = sum(e['amount'] or 0 for e in entries)
    male_count = len([e for e in entries if e['gender'] == 'Male'])
    female_count = len([e for e in entries if e['gender'] == 'Female'])
    other_count = len([e for e in entries if e['gender'] == 'Other'])

    conn.close()

    return render_template(
        'dashboard.html',
        entries=entries,
        total_entries=total_entries,
        total_amount=total_amount,
        male_count=male_count,
        female_count=female_count,
        other_count=other_count,
        username=session.get('username')
    )


# ---------------------------------------------------------
# ADD ENTRY
# ---------------------------------------------------------

@app.route('/add_entry', methods=['POST'])
def add_entry():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    name = request.form['name'].strip()
    gender = request.form['gender']
    amount = request.form['amount']
    date = request.form['date']

    conn = get_db_connection()

    # 🔍 DUPLICATE CHECK
    duplicate = conn.execute("""
        SELECT 1 FROM entries
        WHERE user_id = ?
          AND name = ?
          AND gender = ?
          AND amount = ?
          AND date = ?
    """, (session['user_id'], name, gender, amount, date)).fetchone()

    if duplicate:
        conn.close()
        flash("⚠️ Duplicate entry detected. Entry already exists.", "warning")
        return redirect(url_for('dashboard'))

    # ✅ INSERT IF NOT DUPLICATE
    conn.execute("""
        INSERT INTO entries (user_id, name, gender, amount, date)
        VALUES (?, ?, ?, ?, ?)
    """, (session['user_id'], name, gender, amount, date))

    conn.commit()
    conn.close()

    flash("✅ Entry added successfully!", "success")
    return redirect(url_for('dashboard'))


# ---------------------------------------------------------
# VIEW ENTRY
# ---------------------------------------------------------

@app.route("/view/<int:entry_id>")
@login_required
def view_entry(entry_id):
    conn = get_db_connection()

    if session.get("is_admin"):
        entry = conn.execute(
            "SELECT e.*, u.username AS owner_name FROM entries e JOIN users u ON e.user_id=u.id WHERE e.id=?",
            (entry_id,)
        ).fetchone()
    else:
        entry = conn.execute(
            "SELECT * FROM entries WHERE id=? AND user_id=?",
            (entry_id, session["user_id"])
        ).fetchone()

    conn.close()

    if not entry:
        flash("Entry not found.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("view_entry.html", entry=entry)


# ---------------------------------------------------------
# EDIT ENTRY
# ---------------------------------------------------------

@app.route("/edit/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    conn = get_db_connection()

    if session.get("is_admin"):
        entry = conn.execute("SELECT * FROM entries WHERE id=?", (entry_id,)).fetchone()
    else:
        entry = conn.execute(
            "SELECT * FROM entries WHERE id=? AND user_id=?",
            (entry_id, session["user_id"])
        ).fetchone()

    if not entry:
        conn.close()
        flash("Entry not found.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form["name"]
        gender = request.form["gender"]
        amount = request.form["amount"]
        date = request.form["date"]

        conn.execute(
            "UPDATE entries SET name=?, gender=?, amount=?, date=? WHERE id=?",
            (name, gender, amount, date, entry_id)
        )
        conn.commit()
        conn.close()

        flash("Entry updated!", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("edit_entry.html", entry=entry)


# ---------------------------------------------------------
# DELETE ENTRY
# ---------------------------------------------------------

@app.route("/delete/<int:entry_id>")
@login_required
def delete_entry(entry_id):
    conn = get_db_connection()

    if session.get("is_admin"):
        conn.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    else:
        conn.execute("DELETE FROM entries WHERE id=? AND user_id=?", (entry_id, session["user_id"]))

    conn.commit()
    conn.close()

    flash("Entry deleted.", "info")
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------
# PROFILE
# ---------------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

    if request.method == "POST":
        old = request.form["old_password"]
        new = request.form["new_password"]
        confirm = request.form["confirm_password"]

        if not check_password_hash(user["password"], old):
            flash("Old password incorrect.", "danger")
            conn.close()
            return redirect(url_for("profile"))

        if new != confirm:
            flash("Passwords do not match.", "warning")
            conn.close()
            return redirect(url_for("profile"))

        new_hash = generate_password_hash(new)
        conn.execute("UPDATE users SET password=? WHERE id=?", (new_hash, session["user_id"]))
        conn.commit()
        conn.close()

        flash("Password updated!", "success")
        return redirect(url_for("profile"))

    conn.close()
    return render_template("profile.html", user=user)


# ---------------------------------------------------------
# ADMIN: USERS LIST
# ---------------------------------------------------------

@app.route("/admin")
@admin_required
def admin():
    conn = get_db_connection()
    users = conn.execute("SELECT id, username, email, is_admin FROM users ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin.html", users=users)


@app.route("/admin/promote/<int:user_id>", methods=["POST"])
@admin_required
def admin_promote(user_id):
    conn = get_db_connection()
    conn.execute("UPDATE users SET is_admin=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    flash("User promoted!", "success")
    return redirect(url_for("admin"))


@app.route("/admin/demote/<int:user_id>", methods=["POST"])
@admin_required
def admin_demote(user_id):
    if session["user_id"] == user_id:
        flash("You cannot demote yourself.", "warning")
        return redirect(url_for("admin"))

    conn = get_db_connection()
    conn.execute("UPDATE users SET is_admin=0 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    flash("User demoted.", "info")
    return redirect(url_for("admin"))


@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    if session["user_id"] == user_id:
        flash("You cannot delete your own account.", "warning")
        return redirect(url_for("admin"))

    conn = get_db_connection()
    conn.execute("DELETE FROM entries WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    flash("User deleted.", "info")
    return redirect(url_for("admin"))


# ---------------------------------------------------------
# ADMIN: ENTRIES LIST
# ---------------------------------------------------------

@app.route("/admin/entries")
@admin_required
def admin_entries():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT 
            e.id,
            e.name,
            e.gender,
            e.amount,
            e.date,
            u.username AS owner_name
        FROM entries e
        JOIN users u ON e.user_id=u.id
        ORDER BY e.date DESC
    """).fetchall()
    conn.close()

    return render_template("admin_entries.html", entries=rows)


# ---------------------------------------------------------
# EXPORT DATA
# ---------------------------------------------------------

@app.route("/export/<string:fmt>")
@login_required
def export(fmt):

    conn = get_db_connection()

    if session.get("is_admin"):
        rows = conn.execute("""
            SELECT e.name, e.gender, e.amount, e.date, u.username AS owner_name
            FROM entries e
            JOIN users u ON e.user_id=u.id
            ORDER BY e.date DESC
        """).fetchall()
    else:
        rows = conn.execute("""
            SELECT name, gender, amount, date
            FROM entries
            WHERE user_id=?
            ORDER BY date DESC
        """, (session["user_id"],)).fetchall()

    conn.close()

    df = pd.DataFrame([dict(r) for r in rows])

    if session.get("is_admin"):
        columns = ["owner_name", "name", "gender", "amount", "date"]
        df = df[columns].rename(columns={"owner_name": "User"})
    else:
        df = df[["name", "gender", "amount", "date"]]

    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "csv":
        buf = BytesIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name=f"export_{now_str}.csv")

    if fmt == "xlsx":
        buf = BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name=f"export_{now_str}.xlsx")

    if fmt == "pdf":
        buf = BytesIO()
        p = canvas.Canvas(buf, pagesize=letter)

        width, height = letter
        y = height - 50

        p.setFont("Helvetica-Bold", 12)
        p.drawString(40, y, f"Export: {now_str}")
        y -= 20
        p.setFont("Helvetica", 10)

        header = " | ".join(df.columns)
        p.drawString(40, y, header)
        y -= 15

        for row in df.itertuples(index=False, name=None):
            if y < 40:
                p.showPage()
                y = height - 50
            line = " | ".join([str(col) for col in row])
            p.drawString(40, y, line)
            y -= 15

        p.save()
        buf.seek(0)
        return send_file(buf, as_attachment=True, download_name=f"export_{now_str}.pdf")

    abort(400)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return "OK"
    except Exception as e:
        return f"ERR: {e}"


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run()
