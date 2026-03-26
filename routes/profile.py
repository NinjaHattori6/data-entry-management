from flask import render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from utils.decorators import login_required
from utils.db import get_db_connection

def register_profile_routes(app):

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
