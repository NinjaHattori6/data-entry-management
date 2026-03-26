from flask import render_template
from utils.decorators import login_required
from utils.db import get_db_connection

def register_dashboard_routes(app):

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Display main dashboard with cancer patient statistics"""
        conn = get_db_connection()
        
        # Total patients
        total_patients = conn.execute(
            'SELECT COUNT(*) as count FROM patients'
        ).fetchone()['count']
        
        # Active cases (current_status contains 'Treatment' or 'Under Treatment')
        active_cases = conn.execute(
            'SELECT COUNT(*) as count FROM patients WHERE current_status LIKE ? OR current_status LIKE ?',
            ('%Treatment%', 'Under Treatment')
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
        
        # Recent patients (last 5)
        recent_patients = conn.execute('''
            SELECT * FROM patients 
            ORDER BY created_at DESC 
            LIMIT 5
        ''').fetchall()
        
        # Stage distribution for chart
        stage_data = conn.execute('''
            SELECT cancer_stage, COUNT(*) as count 
            FROM patients 
            GROUP BY cancer_stage
            ORDER BY cancer_stage
        ''').fetchall()
        stage_distribution = {row['cancer_stage']: row['count'] for row in stage_data}
        
        # Status distribution
        status_data = conn.execute('''
            SELECT current_status, COUNT(*) as count 
            FROM patients 
            GROUP BY current_status
            ORDER BY count DESC
        ''').fetchall()
        status_distribution = {row['current_status']: row['count'] for row in status_data}
        
        conn.close()
        
        return render_template('dashboard/dashboard_modern.html', 
                             total_patients=total_patients,
                             active_cases=active_cases,
                             stage_iv_patients=stage_iv_patients,
                             recovered_patients=recovered_patients,
                             recent_patients=recent_patients,
                             stage_distribution=stage_distribution,
                             status_distribution=status_distribution)

    @app.route('/dashboard-sidebar')
    @login_required
    def dashboard_sidebar():
        """Display modern dashboard with sidebar component"""
        conn = get_db_connection()
        
        # Get statistics for sidebar demo
        total_patients = conn.execute(
            'SELECT COUNT(*) as count FROM patients'
        ).fetchone()['count']
        
        conn.close()
        
        # Demo data for the sidebar dashboard
        return render_template('dashboard_sidebar_demo.html', 
                             total_patients=total_patients,
                             appointments_today=8,
                             treatments_completed=24,
                             critical_cases=2)

    @app.route('/analytics')
    @login_required
    def analytics():
        """Display analytics page with charts"""
        conn = get_db_connection()
        
        # Get comprehensive analytics data
        status_data = conn.execute('''
            SELECT current_status, COUNT(*) as count 
            FROM patients 
            GROUP BY current_status
        ''').fetchall()
        status_distribution = {row['current_status']: row['count'] for row in status_data}
        
        cancer_data = conn.execute('''
            SELECT cancer_type, COUNT(*) as count 
            FROM patients 
            GROUP BY cancer_type
        ''').fetchall()
        cancer_distribution = {row['cancer_type']: row['count'] for row in cancer_data}
        
        gender_data = conn.execute('''
            SELECT gender, COUNT(*) as count 
            FROM patients 
            GROUP BY gender
        ''').fetchall()
        gender_distribution = {row['gender']: row['count'] for row in gender_data}
        
        stage_data = conn.execute('''
            SELECT cancer_stage, COUNT(*) as count 
            FROM patients 
            GROUP BY cancer_stage
        ''').fetchall()
        stage_distribution = {row['cancer_stage']: row['count'] for row in stage_data}
        
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
        age_groups = {row['age_group']: row['count'] for row in age_groups}
        
        monthly_trend = conn.execute('''
            SELECT 
                strftime('%Y-%m', diagnosis_date) as month,
                COUNT(*) as count
            FROM patients 
            WHERE diagnosis_date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', diagnosis_date)
            ORDER BY month
        ''').fetchall()
        monthly_trend = {row['month']: row['count'] for row in monthly_trend}
        
        conn.close()
        
        return render_template('dashboard/analytics_modern.html',
                             status_distribution=status_distribution,
                             cancer_distribution=cancer_distribution,
                             gender_distribution=gender_distribution,
                             stage_distribution=stage_distribution,
                             age_groups=age_groups,
                             monthly_trend=monthly_trend)
