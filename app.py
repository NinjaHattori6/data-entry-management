from flask import Flask, render_template
import os
from datetime import datetime
from config_new import Config

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

from utils.db import get_db_connection, generate_patient_id, DATABASE

def init_db():
    """Initialize database if it doesn't exist"""
    if not os.path.exists(DATABASE):
        from init_db import init_database
        init_database()

# Initialize database on app startup
init_db()

# ==================== ROUTE REGISTRATION ====================

# 1. Authentication
from routes.auth import register_auth_routes
register_auth_routes(app)

# 2. Dashboard & Analytics
from routes.dashboard import register_dashboard_routes
register_dashboard_routes(app)

# 3. Patient Records
from routes.patients import register_patient_routes
register_patient_routes(app)

# 4. Admin Management
from routes.admin import register_admin_routes
register_admin_routes(app)

# 5. User Profile
from routes.profile import register_profile_routes
register_profile_routes(app)

# 6. Data Export
from routes.export import register_export_routes
register_export_routes(app)

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
