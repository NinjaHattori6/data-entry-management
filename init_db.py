import sqlite3
import os
from werkzeug.security import generate_password_hash


def init_database():
    """Initialize the database with required tables"""

    db_path = 'oncology_system.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── Users table ──────────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      VARCHAR(80)  UNIQUE NOT NULL,
            full_name     VARCHAR(120),
            email         VARCHAR(120),
            password_hash VARCHAR(255) NOT NULL,
            is_admin      BOOLEAN DEFAULT FALSE,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ── Patients table ────────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE patients (
            id                           INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id                   VARCHAR(20) UNIQUE,
            created_by                   INTEGER NOT NULL,
            full_name                    VARCHAR(100) NOT NULL,
            age                          INTEGER NOT NULL,
            gender                       VARCHAR(10) NOT NULL,
            blood_group                  VARCHAR(5),
            contact_number               VARCHAR(20),
            email                        VARCHAR(120),
            city                         VARCHAR(100),
            state                        VARCHAR(100),
            emergency_contact_name       VARCHAR(100),
            emergency_contact_number     VARCHAR(20),
            cancer_type                  VARCHAR(100) NOT NULL,
            cancer_stage                 VARCHAR(20),
            tumor_size                   FLOAT,
            metastasis                   VARCHAR(10),
            diagnosis_date               DATE NOT NULL,
            treatment_type               VARCHAR(100),
            treatment_phase              VARCHAR(50),
            chemo_cycles_planned         INTEGER,
            chemo_cycles_completed       INTEGER,
            radiation_sessions_planned   INTEGER,
            radiation_sessions_completed INTEGER,
            surgery_status               VARCHAR(50),
            doctor_name                  VARCHAR(100),
            hospital_name                VARCHAR(150),
            height                       FLOAT,
            weight                       FLOAT,
            bmi                          FLOAT,
            blood_pressure               VARCHAR(20),
            heart_rate                   INTEGER,
            risk_level                   VARCHAR(20),
            current_status               VARCHAR(50) NOT NULL,
            next_appointment             DATE,
            notes                        TEXT,
            created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    # ── Indexes ───────────────────────────────────────────────────────────────
    cursor.execute('CREATE INDEX idx_patients_created_by   ON patients(created_by)')
    cursor.execute('CREATE INDEX idx_patients_status       ON patients(current_status)')
    cursor.execute('CREATE INDEX idx_patients_cancer_type  ON patients(cancer_type)')
    cursor.execute('CREATE INDEX idx_patients_cancer_stage ON patients(cancer_stage)')
    cursor.execute('CREATE INDEX idx_patients_patient_id   ON patients(patient_id)')

    # ── Default admin user ────────────────────────────────────────────────────
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (username, full_name, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'Administrator', 'admin@oncology.com', admin_password, True))

    # ── Sample patients ───────────────────────────────────────────────────────
    sample_patients = [
        ('ONC-2024-0001', 1, 'John Smith', 65, 'Male', 'A+', '9876543210',
         'john@email.com', 'Mumbai', 'Maharashtra', 'Jane Smith', '9876543211',
         'Lung Cancer', 'Stage II', 2.5, 'No', '2023-01-15',
         'Chemotherapy', 'Phase 2', 6, 3, 0, 0, 'Not Required',
         'Dr. Sharma', 'Apollo Hospital', 175.0, 70.0, 22.9, '120/80', 72,
         'Medium', 'Under Treatment', '2024-02-01', 'Responding well to chemotherapy'),

        ('ONC-2024-0002', 1, 'Sarah Johnson', 52, 'Female', 'B+', '9876543220',
         'sarah@email.com', 'Delhi', 'Delhi', 'Tom Johnson', '9876543221',
         'Breast Cancer', 'Stage I', 1.2, 'No', '2022-08-20',
         'Radiation', 'Phase 3', 0, 0, 20, 18, 'Completed',
         'Dr. Patel', 'Fortis Hospital', 162.0, 58.0, 22.1, '118/76', 68,
         'Low', 'Remission', '2024-03-15', 'Completed radiation therapy'),

        ('ONC-2024-0003', 1, 'Robert Davis', 71, 'Male', 'O+', '9876543230',
         'robert@email.com', 'Pune', 'Maharashtra', 'Alice Davis', '9876543231',
         'Prostate Cancer', 'Stage III', 3.8, 'No', '2023-03-10',
         'Hormone Therapy', 'Phase 1', 0, 0, 0, 0, 'Not Required',
         'Dr. Mehta', 'Kokilaben Hospital', 168.0, 75.0, 26.6, '130/85', 78,
         'High', 'Under Treatment', '2024-02-20', 'Hormone therapy in progress'),

        ('ONC-2024-0004', 1, 'Maria Garcia', 48, 'Female', 'AB+', '9876543240',
         'maria@email.com', 'Chennai', 'Tamil Nadu', 'Carlos Garcia', '9876543241',
         'Ovarian Cancer', 'Stage IV', 4.5, 'Yes', '2022-11-05',
         'Chemotherapy', 'Phase 4', 8, 8, 0, 0, 'Completed',
         'Dr. Reddy', 'AIIMS Hospital', 158.0, 55.0, 22.0, '125/82', 74,
         'High', 'Relapse', '2024-02-10', 'Recurrence detected, starting new treatment'),

        ('ONC-2024-0005', 1, 'James Wilson', 59, 'Male', 'O-', '9876543250',
         'james@email.com', 'Hyderabad', 'Telangana', 'Mary Wilson', '9876543251',
         'Colon Cancer', 'Stage II', 2.1, 'No', '2022-06-15',
         'Surgery', 'Recovery', 0, 0, 10, 10, 'Completed',
         'Dr. Kumar', 'Yashoda Hospital', 172.0, 80.0, 27.0, '122/78', 70,
         'Low', 'Recovered', '2024-04-01', 'Surgery successful, no signs of recurrence'),
    ]

    cursor.executemany('''
        INSERT INTO patients (
            patient_id, created_by, full_name, age, gender, blood_group,
            contact_number, email, city, state,
            emergency_contact_name, emergency_contact_number,
            cancer_type, cancer_stage, tumor_size, metastasis, diagnosis_date,
            treatment_type, treatment_phase,
            chemo_cycles_planned, chemo_cycles_completed,
            radiation_sessions_planned, radiation_sessions_completed,
            surgery_status, doctor_name, hospital_name,
            height, weight, bmi, blood_pressure, heart_rate,
            risk_level, current_status, next_appointment, notes
        ) VALUES (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )
    ''', sample_patients)

    conn.commit()
    conn.close()

    print("✅ Database initialized successfully!")
    print("👤 Default admin: username=admin  password=admin123")
    print(f"📁 Database: {os.path.abspath(db_path)}")


if __name__ == '__main__':
    init_database()
