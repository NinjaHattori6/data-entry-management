from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, pandas as pd, os, random, smtplib
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ------------------------------------------------------------
# Flask Configuration
# ------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")
DB_NAME = "data_entry.db"


# ------------------------------------------------------------
# Database Utilities
# ------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        is_admin INTEGER DEFAULT 0
                    )''')

    conn.execute('''CREATE TABLE IF NOT EXISTS entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT,
                        gender TEXT,
                        amount REAL,
                        date TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )''')
    conn.commit()
    conn.close()


init_db()


# ------------------------------------------------------------
# Helper: Send Email (demo)
# ------------------------------------------------------------
def send_email(receiver, subject, message):
    """Simple email sender (for demo, replace with Flask-Mail or SMTP setup)"""
    print(f"[EMAIL] To: {receiver}\nSubject: {subject}\nMessage: {message}")


# ------------------------------------------------------------
# Authentication
# ------------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        conn = get_db_connection()
        existing = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            flash("Email already registered.", "warning")
            conn.close()
            return redirect(url_for('login'))

        conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                     (username, email, generate_password_hash(password)))
        conn.commit()
        conn.close()

        flash("Account created successfully!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            flash(f"Welcome, {user['username']}!", "success")
            return redirect(url_for('dashboard'))

        flash("Invalid email or password.", "danger")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# ------------------------------------------------------------
# Forgot / Reset Password Flow
# ------------------------------------------------------------
@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip()
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if not user:
            flash("Email not registered.", "danger")
            return redirect(url_for('forgot_password'))

        otp = str(random.randint(100000, 999999))
        session['reset_email'] = email
        session['otp'] = otp
        send_email(email, "Your OTP Code", f"Your OTP for password reset is: {otp}")

        flash("OTP sent to your email (check console in demo).", "info")
        return redirect(url_for('verify_otp'))

    return render_template('forget.html')


@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp_input = request.form['otp'].strip()
        if otp_input == session.get('otp'):
            session['otp_verified'] = True
            flash("OTP verified successfully.", "success")
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template('otp.html')


@app.route('/reset', methods=['GET', 'POST'])
def reset_password():
    if not session.get('otp_verified'):
        flash("Please verify OTP first.", "warning")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm = request.form['confirm_password']
        email = session.get('reset_email')

        if new_password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('reset_password'))

        conn = get_db_connection()
        conn.execute("UPDATE users SET password=? WHERE email=?",
                     (generate_password_hash(new_password), email))
        conn.commit()
        conn.close()

        session.pop('otp', None)
        session.pop('otp_verified', None)
        session.pop('reset_email', None)
        flash("Password reset successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('reset.html')


# ------------------------------------------------------------
# Dashboard & CRUD
# ------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    entries = conn.execute("SELECT * FROM entries WHERE user_id=? ORDER BY id DESC",
                           (session['user_id'],)).fetchall()
    conn.close()

    total_entries = len(entries)
    total_amount = sum([e['amount'] or 0 for e in entries])
    male_count = len([e for e in entries if e['gender'] == 'Male'])
    female_count = len([e for e in entries if e['gender'] == 'Female'])

    return render_template('dashboard.html',
                           entries=entries,
                           total_entries=total_entries,
                           total_amount=total_amount,
                           male_count=male_count,
                           female_count=female_count,
                           username=session.get('username'))


@app.route('/add_entry', methods=['POST'])
def add_entry():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    name = request.form['name'].strip()
    gender = request.form['gender']
    amount = request.form['amount']
    date = request.form['date']

    if not name or not gender:
        flash("Name and Gender are required.", "warning")
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    conn.execute("INSERT INTO entries (user_id, name, gender, amount, date) VALUES (?, ?, ?, ?, ?)",
                 (session['user_id'], name, gender, amount, date))
    conn.commit()
    conn.close()
    flash("Entry added successfully!", "success")
    return redirect(url_for('dashboard'))


@app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    entry = conn.execute("SELECT * FROM entries WHERE id=? AND user_id=?",
                         (entry_id, session['user_id'])).fetchone()

    if not entry:
        conn.close()
        flash("Entry not found.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        amount = request.form['amount']
        date = request.form['date']
        conn.execute("UPDATE entries SET name=?, gender=?, amount=?, date=? WHERE id=?",
                     (name, gender, amount, date, entry_id))
        conn.commit()
        conn.close()
        flash("Entry updated successfully!", "success")
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('edit_entry.html', entry=entry)


@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM entries WHERE id=? AND user_id=?", (entry_id, session['user_id']))
    conn.commit()
    conn.close()
    flash("Entry deleted successfully.", "info")
    return redirect(url_for('dashboard'))


# ------------------------------------------------------------
# Export Routes
# ------------------------------------------------------------
@app.route('/export/<string:filetype>')
def export_entries(filetype):
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    entries = conn.execute("SELECT name, gender, amount, date FROM entries WHERE user_id=?",
                           (session['user_id'],)).fetchall()
    conn.close()

    df = pd.DataFrame(entries, columns=['name', 'gender', 'amount', 'date'])
    output = BytesIO()

    if filetype == 'csv':
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='entries.csv')

    elif filetype == 'excel':
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return send_file(output,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name='entries.xlsx')

    elif filetype == 'pdf':
        c = canvas.Canvas(output, pagesize=letter)
        width, height = letter
        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(200, y, "User Entries Report")
        y -= 30
        c.setFont("Helvetica", 10)
        for _, row in df.iterrows():
            c.drawString(50, y, f"{row['name']} | {row['gender']} | {row['amount']} | {row['date']}")
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
        output.seek(0)
        return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='entries.pdf')

    flash("Invalid file type.", "danger")
    return redirect(url_for('dashboard'))


# ------------------------------------------------------------
# Profile
# ------------------------------------------------------------
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        old = request.form['old_password']
        new = request.form['new_password']
        confirm = request.form['confirm_password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
        if not check_password_hash(user['password'], old):
            flash("Old password incorrect.", "danger")
        elif new != confirm:
            flash("New passwords do not match.", "warning")
        else:
            conn.execute("UPDATE users SET password=? WHERE id=?",
                         (generate_password_hash(new), session['user_id']))
            conn.commit()
            flash("Password updated successfully!", "success")
        conn.close()

    return render_template('profile.html')


# ------------------------------------------------------------
# Admin Dashboard
# ------------------------------------------------------------
@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    users = conn.execute('''SELECT u.id, u.username, u.email, COUNT(e.id) AS entry_count, u.is_admin
                            FROM users u
                            LEFT JOIN entries e ON u.id = e.user_id
                            GROUP BY u.id''').fetchall()
    conn.close()
    return render_template('admin.html', users=users)


@app.route('/make_admin/<int:user_id>')
def make_admin(user_id):
    if not session.get('is_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    conn.execute("UPDATE users SET is_admin=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    flash("User promoted to admin.", "success")
    return redirect(url_for('admin'))


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if not session.get('is_admin'):
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    conn.execute("DELETE FROM entries WHERE user_id=?", (user_id,))
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    flash("User and their entries deleted.", "info")
    return redirect(url_for('admin'))


# ------------------------------------------------------------
# Error Handlers
# ------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_message="404 - Page Not Found"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_message="500 - Internal Server Error"), 500


# ------------------------------------------------------------
# Run App
# ------------------------------------------------------------
if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=True)
