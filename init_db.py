import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with required tables"""
    
    # Remove existing database if it exists
    db_path = 'oncology_system.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create patients table
    cursor.execute('''
        CREATE TABLE patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL,
            gender VARCHAR(10) NOT NULL,
            cancer_type VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            diagnosis_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX idx_patients_user_id ON patients(user_id)')
    cursor.execute('CREATE INDEX idx_patients_status ON patients(status)')
    cursor.execute('CREATE INDEX idx_patients_cancer_type ON patients(cancer_type)')
    cursor.execute('CREATE INDEX idx_users_email ON users(email)')
    
    # Insert default admin user
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin@oncology.com', admin_password, True))
    
    # Insert sample test data
    sample_patients = [
        (1, 'John Smith', 65, 'Male', 'Lung Cancer', 'Under Treatment', '2023-01-15', 'Patient responding well to chemotherapy'),
        (1, 'Sarah Johnson', 52, 'Female', 'Breast Cancer', 'Remission', '2022-08-20', 'Completed radiation therapy'),
        (1, 'Robert Davis', 71, 'Male', 'Prostate Cancer', 'Under Treatment', '2023-03-10', 'Hormone therapy in progress'),
        (1, 'Maria Garcia', 48, 'Female', 'Ovarian Cancer', 'Relapse', '2022-11-05', 'Recurrence detected, starting new treatment'),
        (1, 'James Wilson', 59, 'Male', 'Colon Cancer', 'Remission', '2022-06-15', 'Surgery successful, no signs of recurrence')
    ]
    
    cursor.executemany('''
        INSERT INTO patients (user_id, name, age, gender, cancer_type, status, diagnosis_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_patients)
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")
    print("Default admin user: admin / admin123")
    print(f"Database created at: {os.path.abspath(db_path)}")

if __name__ == '__main__':
    init_database()
