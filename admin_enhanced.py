"""
Enhanced Admin Routes for Cancer Patient Management System
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, admin_required
import sqlite3
from datetime import datetime

# Database configuration
DATABASE = 'oncology_system.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create admin blueprint
admin_bp = Blueprint('admin_enhanced', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Enhanced admin dashboard with system-wide statistics"""
    conn = get_db_connection()
    
    # System-wide statistics
    total_patients = conn.execute('SELECT COUNT(*) as count FROM patients').fetchone()['count']
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_admins = conn.execute('SELECT COUNT(*) as count FROM users WHERE is_admin = 1').fetchone()['count']
    
    # Recent activity
    recent_patients = conn.execute('''
        SELECT patient_id, full_name, cancer_type, current_status, created_at, created_by
        FROM patients 
        ORDER BY created_at DESC 
        LIMIT 10
    ''').fetchall()
    
    # User activity
    user_activity = conn.execute('''
        SELECT u.username, u.created_at, COUNT(p.id) as patient_count
        FROM users u
        LEFT JOIN patients p ON u.id = p.created_by
        GROUP BY u.id, u.username, u.created_at
        ORDER BY u.created_at DESC
    ''').fetchall()
    
    # Critical patients (Stage IV or Critical status)
    critical_patients = conn.execute('''
        SELECT patient_id, full_name, cancer_type, cancer_stage, current_status, doctor_name
        FROM patients 
        WHERE cancer_stage = 'Stage IV' OR current_status = 'Critical'
        ORDER BY created_at DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/admin_enhanced.html',
                         total_patients=total_patients,
                         total_users=total_users,
                         total_admins=total_admins,
                         recent_patients=recent_patients,
                         user_activity=user_activity,
                         critical_patients=critical_patients)

@admin_bp.route('/bulk_operations', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_operations():
    """Bulk operations for patient management"""
    if request.method == 'POST':
        operation = request.form.get('operation')
        selected_patients = request.form.getlist('selected_patients')
        
        if not selected_patients:
            flash('No patients selected', 'warning')
            return redirect(url_for('admin_enhanced.bulk_operations'))
        
        conn = get_db_connection()
        
        try:
            if operation == 'delete':
                # Bulk delete
                placeholders = ','.join(['?'] * len(selected_patients))
                conn.execute(f'DELETE FROM patients WHERE id IN ({placeholders})', selected_patients)
                flash(f'Deleted {len(selected_patients)} patient records', 'success')
                
            elif operation == 'update_status':
                # Bulk status update
                new_status = request.form.get('new_status')
                placeholders = ','.join(['?'] * len(selected_patients))
                conn.execute(f'UPDATE patients SET current_status = ? WHERE id IN ({placeholders})', 
                           [new_status] + selected_patients)
                flash(f'Updated status for {len(selected_patients)} patients', 'success')
                
            elif operation == 'assign_doctor':
                # Bulk doctor assignment
                doctor_name = request.form.get('doctor_name')
                placeholders = ','.join(['?'] * len(selected_patients))
                conn.execute(f'UPDATE patients SET doctor_name = ? WHERE id IN ({placeholders})', 
                           [doctor_name] + selected_patients)
                flash(f'Assigned doctor to {len(selected_patients)} patients', 'success')
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            flash(f'Error performing bulk operation: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('admin_enhanced.bulk_operations'))
    
    # GET request - show bulk operations interface
    conn = get_db_connection()
    patients = conn.execute('''
        SELECT id, patient_id, full_name, cancer_type, cancer_stage, current_status, doctor_name
        FROM patients 
        ORDER BY created_at DESC
    ''').fetchall()
    
    # Get unique doctors for assignment
    doctors = conn.execute('SELECT DISTINCT doctor_name FROM patients WHERE doctor_name IS NOT NULL').fetchall()
    
    # Get all possible statuses
    statuses = ['Active Treatment', 'Recovered', 'Critical', 'Under Observation', 'Remission', 'Terminal']
    
    conn.close()
    
    return render_template('admin/bulk_operations.html',
                         patients=patients,
                         doctors=doctors,
                         statuses=statuses)

@admin_bp.route('/system_logs')
@login_required
@admin_required
def system_logs():
    """View system activity logs"""
    conn = get_db_connection()
    
    # Get recent patient additions
    recent_additions = conn.execute('''
        SELECT patient_id, full_name, created_by, created_at
        FROM patients 
        ORDER BY created_at DESC 
        LIMIT 20
    ''').fetchall()
    
    # Get recent updates (simplified - in production, you'd have actual logs)
    recent_updates = []  # Placeholder - no updated_at column in current schema
    
    conn.close()
    
    return render_template('admin/system_logs.html',
                         recent_additions=recent_additions,
                         recent_updates=recent_updates)

@admin_bp.route('/database_stats')
@login_required
@admin_required
def database_stats():
    """Database statistics and health"""
    conn = get_db_connection()
    
    # Patient statistics
    patient_stats = {
        'total': conn.execute('SELECT COUNT(*) FROM patients').fetchone()[0],
        'by_status': dict(conn.execute('SELECT current_status, COUNT(*) FROM patients GROUP BY current_status').fetchall()),
        'by_stage': dict(conn.execute('SELECT cancer_stage, COUNT(*) FROM patients GROUP BY cancer_stage').fetchall()),
        'by_type': dict(conn.execute('SELECT cancer_type, COUNT(*) FROM patients GROUP BY cancer_type').fetchall()),
        'by_gender': dict(conn.execute('SELECT gender, COUNT(*) FROM patients GROUP BY gender').fetchall()),
    }
    
    # User statistics
    user_stats = {
        'total': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'admins': conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1').fetchone()[0],
        'regular': conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0],
    }
    
    # Database size (simplified)
    db_size = conn.execute('SELECT COUNT(*) FROM patients UNION ALL SELECT COUNT(*) FROM users').fetchall()
    total_records = sum(row[0] for row in db_size)
    
    conn.close()
    
    return render_template('admin/database_stats.html',
                         patient_stats=patient_stats,
                         user_stats=user_stats,
                         total_records=total_records)

@admin_bp.route('/manage_hospitals')
@login_required
@admin_required
def manage_hospitals():
    """Manage hospitals in the system"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        hospital_name = request.form.get('hospital_name', '').strip()
        action = request.form.get('action')
        
        if action == 'add' and hospital_name:
            # Add new hospital (simplified - in production, you'd have a separate hospitals table)
            flash(f'Hospital "{hospital_name}" would be added to the system', 'info')
        elif action == 'delete':
            hospital_name = request.form.get('hospital_name', '')
            flash(f'Hospital "{hospital_name}" would be removed from the system', 'info')
        
        return redirect(url_for('admin_enhanced.manage_hospitals'))
    
    # Get all unique hospitals from patient data
    hospitals = conn.execute('''
        SELECT DISTINCT hospital_name, COUNT(*) as patient_count
        FROM patients 
        WHERE hospital_name IS NOT NULL
        GROUP BY hospital_name
        ORDER BY patient_count DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/manage_hospitals.html', hospitals=hospitals)

# Register the blueprint
def register_admin_routes(app):
    """Register enhanced admin routes"""
    app.register_blueprint(admin_bp, url_prefix='/admin/enhanced')
