"""
Migration script to create the comprehensive patients table for Oncobloom
Cancer Patient Management System
"""
import sqlite3
import os

def migrate_database():
    """Create new comprehensive patients table"""
    
    db_path = 'oncology_system.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if old patients table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patients'")
    existing_table = cursor.fetchone()
    
    if existing_table:
        # Rename old table to preserve data
        cursor.execute('ALTER TABLE patients RENAME TO patients_old')
        print("📦 Renamed existing 'patients' table to 'patients_old'")
    
    # Create new comprehensive patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            blood_group TEXT,
            contact_number TEXT,
            email TEXT,
            city TEXT,
            state TEXT,
            emergency_contact_name TEXT,
            emergency_contact_number TEXT,
            cancer_type TEXT NOT NULL,
            cancer_stage TEXT NOT NULL,
            tumor_size REAL,
            metastasis TEXT,
            diagnosis_date TEXT,
            treatment_type TEXT,
            treatment_phase TEXT,
            chemo_cycles_planned INTEGER,
            chemo_cycles_completed INTEGER,
            radiation_sessions_planned INTEGER,
            radiation_sessions_completed INTEGER,
            surgery_status TEXT,
            doctor_name TEXT,
            hospital_name TEXT,
            height REAL,
            weight REAL,
            bmi REAL,
            blood_pressure TEXT,
            heart_rate INTEGER,
            risk_level TEXT,
            current_status TEXT,
            next_appointment TEXT,
            created_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Create index on patient_id for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id)
    ''')
    
    # Create index on cancer_stage for dashboard queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_patients_stage ON patients(cancer_stage)
    ''')
    
    # Create index on current_status for dashboard queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_patients_status ON patients(current_status)
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Migration completed successfully!")
    print("📊 New 'patients' table created with comprehensive schema")
    return True

if __name__ == '__main__':
    migrate_database()
