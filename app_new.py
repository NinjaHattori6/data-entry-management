from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import random
import string
from datetime import datetime, timedelta
import pandas as pd
from utils.decorators import login_required, admin_required
from utils.helpers import generate_otp, format_date, export_to_csv, export_to_excel, export_to_pdf
from config_new import Config

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Database configuration
DATABASE = 'oncology_system.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_patient_id():
    """Generate unique patient ID in format ONC-YYYY-0001"""
    conn = get_db_connection()
    current_year = datetime.now().year
    
    # Count existing patients for current year
    count = conn.execute(
        "SELECT COUNT(*) as count FROM patients WHERE patient_id LIKE ?",
        (f'ONC-{current_year}-%',)
    ).fetchone()['count']
    
    conn.close()
    
    # Generate new sequence number (count + 1, zero-padded to 4 digits)
    sequence = count + 1
    patient_id = f"ONC-{current_year}-{sequence:04d}"
    
    return patient_id

def init_db():
    """Initialize database if it doesn't exist"""
    if not os.path.exists(DATABASE):
        from init_db import init_database
        init_database()

# Initialize database on app startup
init_db()

# Import enhanced admin routes
from admin_enhanced import register_admin_routes

# Register enhanced admin routes
register_admin_routes(app)

# ==================== AUTHENTICATION ROUTES ====================

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
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (username, full_name, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?, ?)',
            (username, full_name, password_hash, False, datetime.now())
        )
        conn.commit()
        conn.close()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register_modern.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

# ==================== PASSWORD RESET ROUTES ====================

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password request"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            flash('Please enter your username', 'danger')
            return render_template('auth/forgot_password.html')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user:
            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))
            session['reset_username'] = username
            session['reset_otp'] = otp
            session['otp_expiry'] = datetime.now().timestamp() + 600  # 10 minutes
            
            flash(f'OTP generated: {otp} (In production, this would be sent via secure method)', 'info')
            return redirect(url_for('otp_verify'))
        else:
            flash('No account found with this username', 'danger')
    
    return render_template('auth/forgot_password.html')

@app.route('/otp_verify', methods=['GET', 'POST'])
def otp_verify():
    """Verify OTP for password reset"""
    if 'reset_username' not in session:
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        
        # Check OTP expiry
        if datetime.now().timestamp() > session.get('otp_expiry', 0):
            flash('OTP has expired. Please request a new one', 'danger')
            return redirect(url_for('forgot_password'))
        
        if otp == session.get('reset_otp'):
            flash('OTP verified successfully. Please set your new password', 'success')
            return redirect(url_for('reset_password'))
        else:
            flash('Invalid OTP. Please try again', 'danger')
    
    return render_template('auth/otp_new.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """Reset password after OTP verification"""
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
        session.pop('reset_otp', None)
        session.pop('reset_username', None)
        session.pop('otp_expiry', None)
        
        flash('Password reset successfully! Please login with your new password', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/reset_password.html')

# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Display main dashboard with cancer patient statistics"""
    conn = get_db_connection()
    
    # Get all statistics (no user filtering)
    
    # Total patients
    total_patients = conn.execute(
        'SELECT COUNT(*) as count FROM patients'
    ).fetchone()['count']
    
    # Active cases (current_status = Active Treatment)
    active_cases = conn.execute(
        'SELECT COUNT(*) as count FROM patients WHERE current_status = ?',
        ('Active Treatment',)
    ).fetchone()['count']
    
    # Stage IV patients
    stage_iv_patients = conn.execute(
        'SELECT COUNT(*) as count FROM patients WHERE cancer_stage = ?',
        ('Stage IV',)
    ).fetchone()['count']
    
    # Recovered patients
    recovered_patients = conn.execute(
        'SELECT COUNT(*) as count FROM patients WHERE current_status = ?',
        ('Recovered',)
    ).fetchone()['count']
    
    # Stage distribution for chart
    stage_distribution = conn.execute('''
        SELECT cancer_stage, COUNT(*) as count 
        FROM patients 
        GROUP BY cancer_stage
    ''').fetchall()
    
    # Status distribution
    status_distribution = conn.execute('''
        SELECT current_status, COUNT(*) as count 
        FROM patients 
        GROUP BY current_status
    ''').fetchall()
    
    # Recent patients
    recent_patients = conn.execute('''
        SELECT id, patient_id, full_name, age, gender, cancer_type, cancer_stage, current_status, created_at
        FROM patients 
        ORDER BY created_at DESC 
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard/dashboard_modern.html',
                         total_patients=total_patients,
                         active_cases=active_cases,
                         stage_iv_patients=stage_iv_patients,
                         recovered_patients=recovered_patients,
                         stage_distribution=dict(stage_distribution),
                         status_distribution=dict(status_distribution),
                         recent_patients=recent_patients)

# ==================== PATIENT RECORD ROUTES ====================

@app.route('/records')
@login_required
def records():
    """Display all patient records with new schema"""
    conn = get_db_connection()
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    cancer_filter = request.args.get('cancer_type', '')
    stage_filter = request.args.get('cancer_stage', '')
    search = request.args.get('search', '')
    
    query = '''SELECT id, patient_id, full_name, age, gender, cancer_type, cancer_stage, 
                      current_status, diagnosis_date, doctor_name, created_at
               FROM patients'''
    params = []
    
    # Add WHERE clause if any filters are applied
    where_added = False
    
    if status_filter:
        if not where_added:
            query += ' WHERE current_status = ?'
            where_added = True
        else:
            query += ' AND current_status = ?'
        params.append(status_filter)
    
    if cancer_filter:
        if not where_added:
            query += ' WHERE cancer_type = ?'
            where_added = True
        else:
            query += ' AND cancer_type = ?'
        params.append(cancer_filter)
        
    if stage_filter:
        if not where_added:
            query += ' WHERE cancer_stage = ?'
            where_added = True
        else:
            query += ' AND cancer_stage = ?'
        params.append(stage_filter)
    
    if search:
        if not where_added:
            query += ''' WHERE (full_name LIKE ? OR patient_id LIKE ? OR cancer_type LIKE ? 
                          OR cancer_stage LIKE ? OR doctor_name LIKE ? OR current_status LIKE ?)'''
        else:
            query += ''' AND (full_name LIKE ? OR patient_id LIKE ? OR cancer_type LIKE ? 
                          OR cancer_stage LIKE ? OR doctor_name LIKE ? OR current_status LIKE ?)'''
        search_pattern = f'%{search}%'
        params.extend([search_pattern] * 6)
    
    query += ' ORDER BY created_at DESC'
    
    patients = conn.execute(query, params).fetchall()
    
    # Get unique values for filters
    statuses = conn.execute('SELECT DISTINCT current_status FROM patients').fetchall()
    cancer_types = conn.execute('SELECT DISTINCT cancer_type FROM patients').fetchall()
    stages = conn.execute('SELECT DISTINCT cancer_stage FROM patients').fetchall()
    
    conn.close()
    
    return render_template('dashboard/records_modern.html',
                         patients=patients,
                         statuses=statuses,
                         cancer_types=cancer_types,
                         stages=stages,
                         current_status=status_filter,
                         current_cancer=cancer_filter,
                         current_stage=stage_filter,
                         current_search=search)

@app.route('/add_record', methods=['GET', 'POST'])
@login_required
def add_record():
    """Add a new patient record"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '')
        gender = request.form.get('gender', '')
        cancer_type = request.form.get('cancer_type', '').strip()
        status = request.form.get('status', '')
        diagnosis_date = request.form.get('diagnosis_date', '')
        notes = request.form.get('notes', '').strip()
        
        # Validation
        if not all([name, age, gender, cancer_type, status, diagnosis_date]):
            flash('All required fields must be filled', 'danger')
            return render_template('dashboard/add_record_new.html')
        
        try:
            age = int(age)
            if age <= 0 or age > 150:
                flash('Please enter a valid age', 'danger')
                return render_template('dashboard/add_record_new.html')
        except ValueError:
            flash('Please enter a valid age', 'danger')
            return render_template('dashboard/add_record_new.html')
        
        # Validate diagnosis date
        if diagnosis_date:
            try:
                # Parse the date to ensure it's valid
                from datetime import datetime
                parsed_date = datetime.strptime(diagnosis_date, '%Y-%m-%d')
                
                # Ensure date is not in the future
                if parsed_date > datetime.now():
                    flash('Diagnosis date cannot be in the future', 'danger')
                    return render_template('dashboard/add_record_new.html')
                
                # Ensure date is not too far in the past (e.g., more than 100 years)
                min_date = datetime.now().replace(year=datetime.now().year - 100)
                if parsed_date < min_date:
                    flash('Diagnosis date cannot be more than 100 years in the past', 'danger')
                    return render_template('dashboard/add_record_new.html')
                    
            except ValueError:
                flash('Please enter a valid diagnosis date (YYYY-MM-DD format)', 'danger')
                return render_template('dashboard/add_record_new.html')
        
        # Insert into database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO patients (user_id, name, age, gender, cancer_type, status, diagnosis_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], name, age, gender, cancer_type, status, diagnosis_date, notes))
        conn.commit()
        conn.close()
        
        flash('Patient record added successfully!', 'success')
        return redirect(url_for('records'))
    
    # Get current date for form max date validation
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('dashboard/add_record_new.html', current_date=current_date)

@app.route('/edit_record/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_record(patient_id):
    """Edit an existing patient record"""
    conn = get_db_connection()
    
    # Admin can edit any patient, regular users only their own
    if session.get('is_admin'):
        patient = conn.execute(
            'SELECT * FROM patients WHERE id = ?',
            (patient_id,)
        ).fetchone()
    else:
        patient = conn.execute(
            'SELECT * FROM patients WHERE id = ? AND created_by = ?',
            (patient_id, session['user_id'])
        ).fetchone()
    
    if not patient:
        conn.close()
        flash('Patient record not found', 'danger')
        return redirect(url_for('records'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '')
        gender = request.form.get('gender', '')
        cancer_type = request.form.get('cancer_type', '').strip()
        status = request.form.get('status', '')
        diagnosis_date = request.form.get('diagnosis_date', '')
        notes = request.form.get('notes', '').strip()
        
        # Validation
        if not all([name, age, gender, cancer_type, status, diagnosis_date]):
            flash('All required fields must be filled', 'danger')
            return render_template('dashboard/edit_record_new.html', patient=patient)
        
        try:
            age = int(age)
            if age <= 0 or age > 150:
                flash('Please enter a valid age', 'danger')
                return render_template('dashboard/edit_record_new.html', patient=patient)
        except ValueError:
            flash('Please enter a valid age', 'danger')
            return render_template('dashboard/edit_record_new.html', patient=patient)
        
        # Validate diagnosis date
        if diagnosis_date:
            try:
                # Parse the date to ensure it's valid
                from datetime import datetime
                parsed_date = datetime.strptime(diagnosis_date, '%Y-%m-%d')
                
                # Ensure date is not in the future
                if parsed_date > datetime.now():
                    flash('Diagnosis date cannot be in the future', 'danger')
                    return render_template('dashboard/edit_record_new.html', patient=patient)
                
                # Ensure date is not too far in the past (e.g., more than 100 years)
                min_date = datetime.now().replace(year=datetime.now().year - 100)
                if parsed_date < min_date:
                    flash('Diagnosis date cannot be more than 100 years in the past', 'danger')
                    return render_template('dashboard/edit_record_new.html', patient=patient)
                    
            except ValueError:
                flash('Please enter a valid diagnosis date (YYYY-MM-DD format)', 'danger')
                return render_template('dashboard/edit_record_new.html', patient=patient)
        
        # Update database
        conn.execute('''
            UPDATE patients 
            SET full_name = ?, age = ?, gender = ?, cancer_type = ?, current_status = ?, 
                diagnosis_date = ?
            WHERE id = ? AND created_by = ?
        ''', (name, age, gender, cancer_type, status, diagnosis_date, 
              patient_id, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Patient record updated successfully!', 'success')
        return redirect(url_for('records'))
    
    conn.close()
    
    # Get current date for form max date validation
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('dashboard/edit_record_new.html', patient=patient, current_date=current_date)

@app.route('/delete_record/<int:patient_id>', methods=['POST'])
@login_required
def delete_record(patient_id):
    """Delete a patient record"""
    conn = get_db_connection()
    
    # Admin can delete any patient, regular users only their own
    if session.get('is_admin'):
        patient = conn.execute(
            'SELECT id, full_name FROM patients WHERE id = ?',
            (patient_id,)
        ).fetchone()
        
        if patient:
            conn.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
            conn.commit()
            flash(f'Patient record for {patient["full_name"]} deleted successfully', 'success')
        else:
            flash('Patient record not found', 'danger')
    else:
        # Regular users can only delete their own patients
        patient = conn.execute(
            'SELECT id, full_name FROM patients WHERE id = ? AND created_by = ?',
            (patient_id, session['user_id'])
        ).fetchone()
        
        if patient:
            conn.execute('DELETE FROM patients WHERE id = ? AND created_by = ?', 
                        (patient_id, session['user_id']))
            conn.commit()
            flash(f'Patient record for {patient["full_name"]} deleted successfully', 'success')
        else:
            flash('Patient record not found', 'danger')
    
    conn.close()
    return redirect(url_for('records'))

# ==================== ADD PATIENT ROUTE (COMPREHENSIVE) ====================

@app.route("/add_patient", methods=["GET", "POST"])
@login_required
def add_patient():
    """Add a new patient with comprehensive details"""
    if request.method == "POST":
        # Get all form data
        full_name = request.form.get("full_name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        blood_group = request.form.get("blood_group", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        email = request.form.get("email", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        emergency_contact_name = request.form.get("emergency_contact_name", "").strip()
        emergency_contact_number = request.form.get("emergency_contact_number", "").strip()
        cancer_type = request.form.get("cancer_type", "").strip()
        cancer_stage = request.form.get("cancer_stage", "").strip()
        tumor_size = request.form.get("tumor_size", "").strip()
        metastasis = request.form.get("metastasis", "").strip()
        diagnosis_date = request.form.get("diagnosis_date", "").strip()
        treatment_type = request.form.get("treatment_type", "").strip()
        treatment_phase = request.form.get("treatment_phase", "").strip()
        chemo_cycles_planned = request.form.get("chemo_cycles_planned", "").strip()
        chemo_cycles_completed = request.form.get("chemo_cycles_completed", "").strip()
        radiation_sessions_planned = request.form.get("radiation_sessions_planned", "").strip()
        radiation_sessions_completed = request.form.get("radiation_sessions_completed", "").strip()
        surgery_status = request.form.get("surgery_status", "").strip()
        doctor_name = request.form.get("doctor_name", "").strip()
        hospital_name = request.form.get("hospital_name", "").strip()
        height = request.form.get("height", "").strip()
        weight = request.form.get("weight", "").strip()
        blood_pressure = request.form.get("blood_pressure", "").strip()
        heart_rate = request.form.get("heart_rate", "").strip()
        risk_level = request.form.get("risk_level", "").strip()
        current_status = request.form.get("current_status", "").strip()
        next_appointment = request.form.get("next_appointment", "").strip()

        # Validate required fields
        required_fields = {
            "Full Name": full_name,
            "Age": age,
            "Gender": gender,
            "Cancer Type": cancer_type,
            "Cancer Stage": cancer_stage,
            "Diagnosis Date": diagnosis_date,
            "Current Status": current_status
        }

        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            flash(f"Required fields missing: {', '.join(missing_fields)}", "danger")
            return render_template("add_patient_modern.html")

        # Validate age
        try:
            age = int(age)
            if age <= 0 or age > 150:
                flash("Please enter a valid age (1-150)", "danger")
                return render_template("add_patient_modern.html")
        except ValueError:
            flash("Age must be a valid number", "danger")
            return render_template("add_patient_modern.html")

        # Validate diagnosis date
        if diagnosis_date:
            try:
                # Parse the date to ensure it's valid
                from datetime import datetime
                parsed_date = datetime.strptime(diagnosis_date, '%Y-%m-%d')
                
                # Ensure date is not in the future
                if parsed_date > datetime.now():
                    flash("Diagnosis date cannot be in the future", "danger")
                    return render_template("add_patient_modern.html")
                
                # Ensure date is not too far in the past (e.g., more than 100 years)
                min_date = datetime.now().replace(year=datetime.now().year - 100)
                if parsed_date < min_date:
                    flash("Diagnosis date cannot be more than 100 years in the past", "danger")
                    return render_template("add_patient_modern.html")
                    
            except ValueError:
                flash("Please enter a valid diagnosis date (YYYY-MM-DD format)", "danger")
                return render_template("add_patient_modern.html")

        # Calculate BMI if height and weight provided
        bmi = None
        if height and weight:
            try:
                height_m = float(height) / 100  # Convert cm to meters
                weight_kg = float(weight)
                bmi = round(weight_kg / (height_m ** 2), 2)
            except (ValueError, ZeroDivisionError):
                bmi = None

        # Generate patient ID
        patient_id = generate_patient_id()

        # Get current date for form max date validation
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Convert numeric fields
        try:
            tumor_size = float(tumor_size) if tumor_size else None
        except ValueError:
            tumor_size = None

        try:
            height = float(height) if height else None
        except ValueError:
            height = None

        try:
            weight = float(weight) if weight else None
        except ValueError:
            weight = None

        try:
            heart_rate = int(heart_rate) if heart_rate else None
        except ValueError:
            heart_rate = None

        try:
            chemo_cycles_planned = int(chemo_cycles_planned) if chemo_cycles_planned else None
        except ValueError:
            chemo_cycles_planned = None

        try:
            chemo_cycles_completed = int(chemo_cycles_completed) if chemo_cycles_completed else None
        except ValueError:
            chemo_cycles_completed = None

        try:
            radiation_sessions_planned = int(radiation_sessions_planned) if radiation_sessions_planned else None
        except ValueError:
            radiation_sessions_planned = None

        try:
            radiation_sessions_completed = int(radiation_sessions_completed) if radiation_sessions_completed else None
        except ValueError:
            radiation_sessions_completed = None

        # Insert into database
        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO patients (
                    patient_id, full_name, age, gender, blood_group, contact_number, email,
                    city, state, emergency_contact_name, emergency_contact_number,
                    cancer_type, cancer_stage, tumor_size, metastasis, diagnosis_date,
                    treatment_type, treatment_phase, chemo_cycles_planned, chemo_cycles_completed,
                    radiation_sessions_planned, radiation_sessions_completed, surgery_status,
                    doctor_name, hospital_name, height, weight, bmi, blood_pressure, heart_rate,
                    risk_level, current_status, next_appointment, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_id, full_name, age, gender, blood_group, contact_number, email,
                city, state, emergency_contact_name, emergency_contact_number,
                cancer_type, cancer_stage, tumor_size, metastasis, diagnosis_date,
                treatment_type, treatment_phase, chemo_cycles_planned, chemo_cycles_completed,
                radiation_sessions_planned, radiation_sessions_completed, surgery_status,
                doctor_name, hospital_name, height, weight, bmi, blood_pressure, heart_rate,
                risk_level, current_status, next_appointment, session["user_id"]
            ))
            conn.commit()
            flash(f"Patient {full_name} registered successfully with ID: {patient_id}", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            conn.rollback()
            flash(f"Error registering patient: {str(e)}", "danger")
            return render_template("add_patient_modern.html")
        finally:
            conn.close()

    # Get current date for form max date validation
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')

    return render_template("add_patient_modern.html", current_date=current_date)

# ==================== ANALYTICS ROUTES ====================

@app.route('/analytics')
@login_required
def analytics():
    """Display analytics page with charts"""
    conn = get_db_connection()
    
    # Get comprehensive analytics data
    status_distribution = conn.execute('''
        SELECT current_status, COUNT(*) as count 
        FROM patients 
        GROUP BY current_status
    ''').fetchall()
    
    cancer_distribution = conn.execute('''
        SELECT cancer_type, COUNT(*) as count 
        FROM patients 
        GROUP BY cancer_type
    ''').fetchall()
    
    gender_distribution = conn.execute('''
        SELECT gender, COUNT(*) as count 
        FROM patients 
        GROUP BY gender
    ''').fetchall()
    
    stage_distribution = conn.execute('''
        SELECT cancer_stage, COUNT(*) as count 
        FROM patients 
        GROUP BY cancer_stage
    ''').fetchall()
    
    age_groups = conn.execute('''
        SELECT 
            CASE 
                WHEN age < 18 THEN 'Under 18'
                WHEN age BETWEEN 18 AND 35 THEN '18-35'
                WHEN age BETWEEN 36 AND 50 THEN '36-50'
                WHEN age BETWEEN 51 AND 65 THEN '51-65'
                ELSE 'Over 65'
            END as age_group,
            COUNT(*) as count
        FROM patients 
        GROUP BY age_group
    ''').fetchall()
    
    monthly_trend = conn.execute('''
        SELECT 
            strftime('%Y-%m', diagnosis_date) as month,
            COUNT(*) as count
        FROM patients 
        WHERE diagnosis_date >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', diagnosis_date)
        ORDER BY month
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard/analytics_modern.html',
                         status_distribution=status_distribution,
                         cancer_distribution=cancer_distribution,
                         gender_distribution=gender_distribution,
                         stage_distribution=stage_distribution,
                         age_groups=age_groups,
                         monthly_trend=monthly_trend)

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
@admin_required
def admin():
    """Display admin panel"""
    conn = get_db_connection()
    
    # Get all users
    users = conn.execute('''
        SELECT id, username, full_name, is_admin, created_at,
               (SELECT COUNT(*) FROM patients WHERE created_by = users.id) as patient_count
        FROM users 
        ORDER BY created_at DESC
    ''').fetchall()
    
    # Get system statistics
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_patients = conn.execute('SELECT COUNT(*) as count FROM patients').fetchone()['count']
    total_admins = conn.execute('SELECT COUNT(*) as count FROM users WHERE is_admin = 1').fetchone()['count']
    
    conn.close()
    
    return render_template('admin/admin_modern.html',
                         users=users,
                         total_users=total_users,
                         total_patients=total_patients,
                         total_admins=total_admins)

@app.route('/admin/promote/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_promote(user_id):
    """Promote a user to admin"""
    conn = get_db_connection()
    
    # Update user to admin
    conn.execute('UPDATE users SET is_admin = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    flash('User promoted to admin successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/demote/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_demote(user_id):
    """Demote an admin to regular user"""
    conn = get_db_connection()
    
    # Prevent demoting yourself
    if user_id == session['user_id']:
        flash('You cannot demote yourself', 'danger')
        return redirect(url_for('admin'))
    
    # Update user to regular user
    conn.execute('UPDATE users SET is_admin = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    flash('User demoted to regular user successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Delete a user from the system"""
    conn = get_db_connection()
    
    # Prevent deleting yourself
    if user_id == session['user_id']:
        flash('You cannot delete yourself', 'danger')
        return redirect(url_for('admin'))
    
    # Check if user exists
    user = conn.execute('SELECT id, username FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        conn.close()
        flash('User not found', 'danger')
        return redirect(url_for('admin'))
    
    # Delete user's patients first (cascade)
    conn.execute('DELETE FROM patients WHERE created_by = ?', (user_id,))
    
    # Delete the user
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    flash(f'User {user["username"]} deleted successfully', 'success')
    return redirect(url_for('admin'))

# ==================== PROFILE ROUTE ====================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Display and update user profile"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Get current user data
        user = conn.execute('SELECT * FROM users WHERE id = ?', 
                          (session['user_id'],)).fetchone()
        
        # Update password if provided
        if new_password:
            if not current_password:
                flash('Current password is required to change password', 'danger')
                return render_template('dashboard/profile_new.html', user=user)
            
            if not check_password_hash(user['password_hash'], current_password):
                flash('Current password is incorrect', 'danger')
                return render_template('dashboard/profile_new.html', user=user)
            
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long', 'danger')
                return render_template('dashboard/profile_new.html', user=user)
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return render_template('dashboard/profile_new.html', user=user)
            
            conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                        (generate_password_hash(new_password), session['user_id']))
            conn.commit()
            flash('Password updated successfully', 'success')
        
        conn.close()
        return redirect(url_for('profile'))
    
    # GET request - display profile
    user = conn.execute('SELECT * FROM users WHERE id = ?', 
                      (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('dashboard/profile_new.html', user=user)

# ==================== EXPORT ROUTE ====================

@app.route('/export_data', methods=['POST'])
@login_required
def export_data():
    """Export patient data in various formats"""
    export_format = request.form.get('format', 'csv')
    
    conn = get_db_connection()
    
    # Get filtered data based on current filters
    status_filter = request.form.get('status', '')
    cancer_filter = request.form.get('cancer_type', '')
    search = request.form.get('search', '')
    
    query = '''
        SELECT patient_id, full_name, age, gender, cancer_type, cancer_stage, 
               current_status, diagnosis_date, doctor_name, hospital_name, created_at
        FROM patients 
    '''
    params = []
    
    if status_filter:
        query += ' AND current_status = ?'
        params.append(status_filter)
    
    if cancer_filter:
        query += ' AND cancer_type = ?'
        params.append(cancer_filter)
    
    if search:
        query += ' AND (full_name LIKE ? OR patient_id LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY created_at DESC'
    
    patients = conn.execute(query, params).fetchall()
    conn.close()
    
    # Convert to list of dictionaries for export
    data = []
    for patient in patients:
        data.append({
            'Patient ID': patient['patient_id'],
            'Full Name': patient['full_name'],
            'Age': patient['age'],
            'Gender': patient['gender'],
            'Cancer Type': patient['cancer_type'],
            'Stage': patient['cancer_stage'],
            'Status': patient['current_status'],
            'Diagnosis Date': patient['diagnosis_date'],
            'Doctor': patient['doctor_name'],
            'Hospital': patient['hospital_name'],
            'Created At': patient['created_at']
        })
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        if export_format == 'csv':
            filename = f'patients_{timestamp}.csv'
            filepath = export_to_csv(data, filename)
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        elif export_format == 'excel':
            filename = f'patients_{timestamp}.xlsx'
            filepath = export_to_excel(data, filename)
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        elif export_format == 'pdf':
            filename = f'patients_{timestamp}.pdf'
            filepath = export_to_pdf(data, filename, 'Patient Records Report')
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        else:
            flash('Invalid export format', 'danger')
            return redirect(url_for('records'))
    
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'danger')
        return redirect(url_for('records'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_code=404,
                         error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html', 
                         error_code=500,
                         error_message='Internal server error'), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
