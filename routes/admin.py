from flask import render_template, request, flash, redirect, url_for, session
from utils.decorators import login_required, admin_required
from utils.db import get_db_connection

def register_admin_routes(app):

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
        if user_id == session['user_id']:
            flash('You cannot demote yourself', 'danger')
            return redirect(url_for('admin'))
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
        if user_id == session['user_id']:
            flash('You cannot delete yourself', 'danger')
            return redirect(url_for('admin'))
        user = conn.execute('SELECT id, username FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            conn.close()
            flash('User not found', 'danger')
            return redirect(url_for('admin'))
        conn.execute('DELETE FROM patients WHERE created_by = ?', (user_id,))
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        flash(f'User {user["username"]} deleted successfully', 'success')
        return redirect(url_for('admin'))

    # Enhanced Admin Routes
    @app.route('/admin/enhanced/dashboard')
    @login_required
    @admin_required
    def admin_enhanced_dashboard():
        """Enhanced admin dashboard with system-wide statistics"""
        conn = get_db_connection()
        total_patients = conn.execute('SELECT COUNT(*) as count FROM patients').fetchone()['count']
        total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
        total_admins = conn.execute('SELECT COUNT(*) as count FROM users WHERE is_admin = 1').fetchone()['count']
        recent_patients = conn.execute('''
            SELECT patient_id, full_name, cancer_type, current_status, created_at, created_by
            FROM patients ORDER BY created_at DESC LIMIT 10
        ''').fetchall()
        user_activity = conn.execute('''
            SELECT u.username, u.created_at, COUNT(p.id) as patient_count
            FROM users u
            LEFT JOIN patients p ON u.id = p.created_by
            GROUP BY u.id, u.username, u.created_at
            ORDER BY u.created_at DESC
        ''').fetchall()
        critical_patients = conn.execute('''
            SELECT patient_id, full_name, cancer_type, cancer_stage, current_status, doctor_name
            FROM patients WHERE cancer_stage = 'Stage IV' OR current_status = 'Critical'
            ORDER BY created_at DESC LIMIT 5
        ''').fetchall()
        conn.close()
        return render_template('admin/admin_enhanced.html', total_patients=total_patients, total_users=total_users,
                             total_admins=total_admins, recent_patients=recent_patients, user_activity=user_activity,
                             critical_patients=critical_patients)

    @app.route('/admin/enhanced/bulk_operations', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_bulk_operations():
        """Bulk operations for patient management"""
        if request.method == 'POST':
            operation = request.form.get('operation')
            selected_patients = request.form.getlist('selected_patients')
            if not selected_patients:
                flash('No patients selected', 'warning')
                return redirect(url_for('admin_bulk_operations'))
            conn = get_db_connection()
            try:
                if operation == 'delete':
                    placeholders = ','.join(['?'] * len(selected_patients))
                    conn.execute(f'DELETE FROM patients WHERE id IN ({placeholders})', selected_patients)
                    flash(f'Deleted {len(selected_patients)} patient records', 'success')
                elif operation == 'update_status':
                    new_status = request.form.get('new_status')
                    placeholders = ','.join(['?'] * len(selected_patients))
                    conn.execute(f'UPDATE patients SET current_status = ? WHERE id IN ({placeholders})', [new_status] + selected_patients)
                    flash(f'Updated status for {len(selected_patients)} patients', 'success')
                elif operation == 'assign_doctor':
                    doctor_name = request.form.get('doctor_name')
                    placeholders = ','.join(['?'] * len(selected_patients))
                    conn.execute(f'UPDATE patients SET doctor_name = ? WHERE id IN ({placeholders})', [doctor_name] + selected_patients)
                    flash(f'Assigned doctor to {len(selected_patients)} patients', 'success')
                conn.commit()
            except Exception as e:
                conn.rollback()
                flash(f'Error performing bulk operation: {str(e)}', 'danger')
            finally:
                conn.close()
            return redirect(url_for('admin_bulk_operations'))
        conn = get_db_connection()
        patients = conn.execute('SELECT id, patient_id, full_name, cancer_type, cancer_stage, current_status, doctor_name FROM patients ORDER BY created_at DESC').fetchall()
        doctors = conn.execute('SELECT DISTINCT doctor_name FROM patients WHERE doctor_name IS NOT NULL').fetchall()
        statuses = ['Active Treatment', 'Recovered', 'Critical', 'Under Observation', 'Remission', 'Terminal']
        conn.close()
        return render_template('admin/bulk_operations.html', patients=patients, doctors=doctors, statuses=statuses)

    @app.route('/admin/enhanced/system_logs')
    @login_required
    @admin_required
    def admin_system_logs():
        """View system activity logs"""
        conn = get_db_connection()
        recent_additions = conn.execute('SELECT patient_id, full_name, created_by, created_at FROM patients ORDER BY created_at DESC LIMIT 20').fetchall()
        conn.close()
        return render_template('admin/system_logs.html', recent_additions=recent_additions, recent_updates=[])

    @app.route('/admin/enhanced/database_stats')
    @login_required
    @admin_required
    def admin_database_stats():
        """Database statistics and health"""
        conn = get_db_connection()
        patient_stats = {
            'total': conn.execute('SELECT COUNT(*) FROM patients').fetchone()[0],
            'by_status': dict(conn.execute('SELECT current_status, COUNT(*) FROM patients GROUP BY current_status').fetchall()),
            'by_stage': dict(conn.execute('SELECT cancer_stage, COUNT(*) FROM patients GROUP BY cancer_stage').fetchall()),
            'by_type': dict(conn.execute('SELECT cancer_type, COUNT(*) FROM patients GROUP BY cancer_type').fetchall()),
            'by_gender': dict(conn.execute('SELECT gender, COUNT(*) FROM patients GROUP BY gender').fetchall()),
        }
        user_stats = {
            'total': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
            'admins': conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1').fetchone()[0],
            'regular': conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0],
        }
        db_size = conn.execute('SELECT COUNT(*) FROM patients UNION ALL SELECT COUNT(*) FROM users').fetchall()
        total_records = sum(row[0] for row in db_size)
        conn.close()
        return render_template('admin/database_stats.html', patient_stats=patient_stats, user_stats=user_stats, total_records=total_records)

    @app.route('/admin/enhanced/manage_hospitals', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_manage_hospitals():
        """Manage hospitals in the system"""
        conn = get_db_connection()
        if request.method == 'POST':
            hospital_name = request.form.get('hospital_name', '').strip()
            action = request.form.get('action')
            if action == 'add' and hospital_name:
                flash(f'Hospital "{hospital_name}" would be added to the system', 'info')
            elif action == 'delete':
                hospital_name = request.form.get('hospital_name', '')
                flash(f'Hospital "{hospital_name}" would be removed from the system', 'info')
            return redirect(url_for('admin_manage_hospitals'))
        hospitals = conn.execute('SELECT DISTINCT hospital_name, COUNT(*) as patient_count FROM patients WHERE hospital_name IS NOT NULL GROUP BY hospital_name ORDER BY patient_count DESC').fetchall()
        conn.close()
        return render_template('admin/manage_hospitals.html', hospitals=hospitals)
