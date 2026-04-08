import sqlite3
import os
from werkzeug.security import generate_password_hash


def init_database():
    """Initialize the database with required tables (safe and idempotent)."""

    # Allow configuring the DB path via an environment variable
    db_path = os.environ.get('DB_PATH', 'oncology_system.db')

    # Create parent directory if needed (e.g. /data/oncology_system.db on a
    # Render persistent disk)
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── Users table ──────────────────────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
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
        CREATE TABLE IF NOT EXISTS patients (
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
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_created_by   ON patients(created_by)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_status       ON patients(current_status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_cancer_type  ON patients(cancer_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_cancer_stage ON patients(cancer_stage)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_patient_id   ON patients(patient_id)')

    # ── Default admin user (only if it doesn't already exist) ────────────────
    existing = cursor.execute(
        'SELECT id FROM users WHERE username = ?', ('admin',)
    ).fetchone()
    if not existing:
        raw_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
        if not os.environ.get('DEFAULT_ADMIN_PASSWORD'):
            print("⚠️  DEFAULT_ADMIN_PASSWORD env var is not set. "
                  "Using insecure default — please set a strong password before going live.")
        admin_password = generate_password_hash(raw_password)
        cursor.execute('''
            INSERT INTO users (username, full_name, email, password_hash, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'Administrator', 'admin@oncology.com', admin_password, True))
        print("✅ Database initialized successfully!")
        print("👤 Default admin user created: username=admin")
        print("   (password set from DEFAULT_ADMIN_PASSWORD env var or default)")
    else:
        print("✅ Database schema verified successfully!")

    conn.commit()
    conn.close()

    print(f"📁 Database: {os.path.abspath(db_path)}")


if __name__ == '__main__':
    init_database()
