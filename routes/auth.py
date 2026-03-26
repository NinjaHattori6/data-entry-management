from flask import render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from utils.db import get_db_connection
import secrets

def register_auth_routes(app):

    @app.route('/')
    def index():
        """Show landing page"""
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login"""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Please enter both username and password', 'danger')
                return render_template('auth/login_modern.html')
            
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = bool(user['is_admin'])
                session.permanent = True
                
                flash(f'Welcome back, {user["username"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        
        return render_template('auth/login_modern.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Handle user registration"""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            full_name = request.form.get('full_name', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            if not username or len(username) < 3:
                flash('Username must be at least 3 characters long', 'danger')
                return render_template('auth/register_modern.html')
            
            if not full_name or len(full_name) < 2:
                flash('Please enter your full name', 'danger')
                return render_template('auth/register_modern.html')
            
            if not password or len(password) < 6:
                flash('Password must be at least 6 characters long', 'danger')
                return render_template('auth/register_modern.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('auth/register_modern.html')
            
            # Check if user already exists
            conn = get_db_connection()
            existing_user = conn.execute(
                'SELECT id FROM users WHERE username = ?', 
                (username,)
            ).fetchone()
            
            if existing_user:
                conn.close()
                flash('Username already exists', 'danger')
                return render_template('auth/register_modern.html')
            
            # Generate a unique recovery key
            recovery_key = "OB-" + secrets.token_hex(8).upper()
            recovery_key_hash = generate_password_hash(recovery_key)
            
            # Create new user
            password_hash = generate_password_hash(password)
            conn.execute(
                'INSERT INTO users (username, full_name, password_hash, recovery_key_hash, is_admin, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (username, full_name, password_hash, recovery_key_hash, False, datetime.now())
            )
            conn.commit()
            conn.close()
            
            # Don't redirect to login yet, show them their recovery key
            return render_template('auth/register_success_modern.html', username=username, recovery_key=recovery_key)
        
        return render_template('auth/register_modern.html')

    @app.route('/logout')
    def logout():
        """Handle user logout"""
        session.clear()
        flash('You have been logged out successfully', 'info')
        return redirect(url_for('login'))

    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        """Handle forgot password request"""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            recovery_key = request.form.get('recovery_key', '').strip()
            
            if not username or not recovery_key:
                flash('Please enter both username and recovery key', 'danger')
                return render_template('auth/forgot_password.html')
            
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            
            if user and user['recovery_key_hash'] and check_password_hash(user['recovery_key_hash'], recovery_key):
                # Recovery key is valid, log them in for password reset
                session['reset_username'] = username
                flash('Recovery Key verified. Please set your new password.', 'success')
                return redirect(url_for('reset_password'))
            else:
                flash('Invalid username or recovery key', 'danger')
        
        return render_template('auth/forgot_password.html')

    @app.route('/reset_password', methods=['GET', 'POST'])
    def reset_password():
        """Reset password after key verification"""
        if 'reset_username' not in session:
            return redirect(url_for('forgot_password'))
        
        if request.method == 'POST':
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not password or len(password) < 6:
                flash('Password must be at least 6 characters long', 'danger')
                return render_template('auth/reset_password.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('auth/reset_password.html')
            
            # Update password in database
            conn = get_db_connection()
            conn.execute(
                'UPDATE users SET password_hash = ? WHERE username = ?',
                (generate_password_hash(password), session['reset_username'])
            )
            conn.commit()
            conn.close()
            
            # Clear reset session
            session.pop('reset_username', None)
            
            flash('Password reset successfully! Please login with your new password', 'success')
            return redirect(url_for('login'))
        
        return render_template('auth/reset_password.html')
