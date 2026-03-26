from flask import request, flash, redirect, url_for, send_file
from datetime import datetime
from utils.decorators import login_required
from utils.db import get_db_connection
from utils.helpers import export_to_csv, export_to_excel, export_to_pdf

def register_export_routes(app):

    @app.route('/export_data', methods=['GET', 'POST'])
    @login_required
    def export_data():
        """Export patient data in various formats"""
        export_format = request.args.get('format') or request.form.get('format', 'csv')
        
        conn = get_db_connection()
        
        # Get filtered data based on current filters
        status_filter = request.args.get('status') or request.form.get('status', '')
        cancer_filter = request.args.get('cancer_type') or request.form.get('cancer_type', '')
        search = request.args.get('search') or request.form.get('search', '')
        
        query = '''
            SELECT patient_id, full_name, age, gender, cancer_type, cancer_stage, 
                   current_status, diagnosis_date, doctor_name, hospital_name, created_at
            FROM patients 
            WHERE 1=1
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
