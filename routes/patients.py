import re
from flask import render_template, request, flash, redirect, url_for, session
from datetime import datetime
from utils.decorators import login_required
from utils.db import get_db_connection, generate_patient_id

def register_patient_routes(app):

    @app.route('/records')
    @login_required
    def records():
        """Display all patient records"""
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
                    parsed_date = datetime.strptime(diagnosis_date, '%Y-%m-%d')
                    if parsed_date > datetime.now():
                        flash('Diagnosis date cannot be in the future', 'danger')
                        return render_template('dashboard/add_record_new.html')
                    
                    min_date = datetime.now().replace(year=datetime.now().year - 100)
                    if parsed_date < min_date:
                        flash('Diagnosis date cannot be more than 100 years in the past', 'danger')
                        return render_template('dashboard/add_record_new.html')
                except ValueError:
                    flash('Please enter a valid diagnosis date', 'danger')
                    return render_template('dashboard/add_record_new.html')
            
            # Insert into database
            conn = get_db_connection()
            patient_id = generate_patient_id()
            conn.execute('''
                INSERT INTO patients (patient_id, created_by, full_name, age, gender, cancer_type, current_status, diagnosis_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, session['user_id'], name, age, gender, cancer_type, status, diagnosis_date, notes))
            conn.commit()
            conn.close()
            
            flash('Patient record added successfully!', 'success')
            return redirect(url_for('records'))
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('dashboard/add_record_new.html', current_date=current_date)

    @app.route('/edit_record/<int:patient_id>', methods=['GET', 'POST'])
    @login_required
    def edit_record(patient_id):
        """Edit an existing patient record"""
        conn = get_db_connection()
        
        if session.get('is_admin'):
            patient = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,)).fetchone()
        else:
            patient = conn.execute('SELECT * FROM patients WHERE id = ? AND created_by = ?', (patient_id, session['user_id'])).fetchone()
        
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
            
            if diagnosis_date:
                try:
                    parsed_date = datetime.strptime(diagnosis_date, '%Y-%m-%d')
                    if parsed_date > datetime.now():
                        flash('Diagnosis date cannot be in the future', 'danger')
                        return render_template('dashboard/edit_record_new.html', patient=patient)
                    
                    min_date = datetime.now().replace(year=datetime.now().year - 100)
                    if parsed_date < min_date:
                        flash('Diagnosis date cannot be more than 100 years in the past', 'danger')
                        return render_template('dashboard/edit_record_new.html', patient=patient)
                except ValueError:
                    flash('Please enter a valid diagnosis date (YYYY-MM-DD format)', 'danger')
                    return render_template('dashboard/edit_record_new.html', patient=patient)
            
            if session.get('is_admin'):
                conn.execute('''
                    UPDATE patients
                    SET full_name=?, age=?, gender=?, cancer_type=?,
                        current_status=?, diagnosis_date=?, notes=?
                    WHERE id=?
                ''', (name, age, gender, cancer_type, status, diagnosis_date, notes, patient_id))
            else:
                conn.execute('''
                    UPDATE patients
                    SET full_name=?, age=?, gender=?, cancer_type=?,
                        current_status=?, diagnosis_date=?, notes=?
                    WHERE id=? AND created_by=?
                ''', (name, age, gender, cancer_type, status, diagnosis_date, notes, patient_id, session['user_id']))
            conn.commit()
            conn.close()
            
            flash('Patient record updated successfully!', 'success')
            return redirect(url_for('records'))
        
        conn.close()
        current_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('dashboard/edit_record_new.html', patient=patient, current_date=current_date)

    @app.route('/delete_record/<int:patient_id>', methods=['POST'])
    @login_required
    def delete_record(patient_id):
        """Delete a patient record"""
        conn = get_db_connection()
        
        if session.get('is_admin'):
            patient = conn.execute('SELECT id, full_name FROM patients WHERE id = ?', (patient_id,)).fetchone()
            if patient:
                conn.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
                conn.commit()
                flash(f'Patient record for {patient["full_name"]} deleted successfully', 'success')
            else:
                flash('Patient record not found', 'danger')
        else:
            patient = conn.execute('SELECT id, full_name FROM patients WHERE id = ? AND created_by = ?', (patient_id, session['user_id'])).fetchone()
            if patient:
                conn.execute('DELETE FROM patients WHERE id = ? AND created_by = ?', (patient_id, session['user_id']))
                conn.commit()
                flash(f'Patient record for {patient["full_name"]} deleted successfully', 'success')
            else:
                flash('Patient record not found', 'danger')
        
        conn.close()
        return redirect(url_for('records'))

    @app.route("/add_patient", methods=["GET", "POST"])
    @login_required
    def add_patient():
        """Add a new patient with comprehensive details"""
        if request.method == "POST":
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
                return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))

            try:
                age = int(age)
                if age <= 0 or age > 150:
                    flash("Please enter a valid age (1-150)", "danger")
                    return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
            except ValueError:
                flash("Age must be a valid number", "danger")
                return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))

            if email:
                email_pattern = re.compile(r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$')
                if not email_pattern.match(email):
                    flash("Please enter a valid email address", "danger")
                    return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))

            if diagnosis_date:
                try:
                    parsed_date = datetime.strptime(diagnosis_date, '%Y-%m-%d')
                    if parsed_date > datetime.now():
                        flash("Diagnosis date cannot be in the future", "danger")
                        return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
                    
                    min_date = datetime.now().replace(year=datetime.now().year - 100)
                    if parsed_date < min_date:
                        flash("Diagnosis date cannot be more than 100 years in the past", "danger")
                        return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
                except ValueError:
                    flash("Please enter a valid diagnosis date", "danger")
                    return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))

            if contact_number and (not contact_number.isdigit() or len(contact_number) != 10):
                flash("Please enter a valid 10-digit phone number for Contact Number", "danger")
                return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))

            if emergency_contact_number and (not emergency_contact_number.isdigit() or len(emergency_contact_number) != 10):
                flash("Please enter a valid 10-digit phone number for Emergency Contact Number", "danger")
                return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
            if blood_pressure:
                bp_pattern = re.compile(r'^\d{1,3}/\d{1,3}$')
                if not bp_pattern.match(blood_pressure):
                    flash("Blood pressure must be in systolic/diastolic format (e.g., 120/80)", "danger")
                    return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))

            if next_appointment:
                try:
                    parsed_appt = datetime.strptime(next_appointment, '%Y-%m-%d')
                    if parsed_appt.date() < datetime.now().date():
                        flash("Next appointment date cannot be in the past", "danger")
                        return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
                except ValueError:
                    flash("Please enter a valid next appointment date", "danger")
                    return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))

            bmi = None
            if height and weight:
                try:
                    height_m = float(height) / 100
                    weight_kg = float(weight)
                    bmi = round(weight_kg / (height_m ** 2), 2)
                except (ValueError, ZeroDivisionError):
                    bmi = None

            patient_id = generate_patient_id()

            try:
                tumor_size = float(tumor_size) if tumor_size else None
                if tumor_size is not None and tumor_size <= 0:
                    flash("Tumor size must be a positive number", "danger")
                    return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
            except ValueError:
                tumor_size = None

            try:
                height = float(height) if height else None
                if height is not None and height <= 0:
                    flash("Height must be a positive number", "danger")
                    return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
            except ValueError:
                height = None

            try:
                weight = float(weight) if weight else None
                if weight is not None and weight <= 0:
                    flash("Weight must be a positive number", "danger")
                    return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
            except ValueError:
                weight = None

            try:
                heart_rate = int(heart_rate) if heart_rate else None
                if heart_rate is not None and heart_rate <= 0:
                    flash("Heart rate must be a positive number", "danger")
                    return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
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
                return render_template("add_patient_modern.html", current_date=datetime.now().strftime('%Y-%m-%d'))
            finally:
                conn.close()

        current_date = datetime.now().strftime('%Y-%m-%d')
        return render_template("add_patient_modern.html", current_date=current_date)
