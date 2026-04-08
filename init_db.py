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
            recovery_key_hash VARCHAR(255),
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

    conn.commit()
    conn.close()

    print("✅ Database initialized successfully!")
    print("👤 Default admin: username=admin  password=admin123")
    print(f"📁 Database: {os.path.abspath(db_path)}")


if __name__ == '__main__':
    init_database()
