import sqlite3
import os
from datetime import datetime

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
