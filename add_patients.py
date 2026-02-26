import sqlite3
from datetime import datetime, timedelta
import random

def add_sample_patients():
    """Add 20 sample patient records to the database"""
    
    conn = sqlite3.connect('oncology_system.db')
    cursor = conn.cursor()
    
    # Sample data for generating patients
    first_names = ['John', 'Sarah', 'Robert', 'Maria', 'James', 'Jennifer', 'Michael', 'Linda', 'William', 'Patricia',
                   'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Karen', 'Charles', 'Nancy']
    
    last_names = ['Smith', 'Johnson', 'Davis', 'Garcia', 'Wilson', 'Miller', 'Brown', 'Jones', 'Taylor', 'Anderson',
                  'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Gonzalez', 'Murphy', 'Robinson', 'Clark']
    
    cancer_types = ['Lung Cancer', 'Breast Cancer', 'Prostate Cancer', 'Ovarian Cancer', 'Colon Cancer',
                    'Skin Cancer', 'Brain Cancer', 'Liver Cancer', 'Pancreatic Cancer', 'Leukemia',
                    'Lymphoma', 'Kidney Cancer', 'Stomach Cancer', 'Bladder Cancer', 'Thyroid Cancer']
    
    statuses = ['Under Treatment', 'Remission', 'Relapse', 'Newly Diagnosed', 'Terminal']
    genders = ['Male', 'Female']
    
    # Generate 20 patient records
    patients = []
    for i in range(20):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        age = random.randint(35, 78)
        gender = random.choice(genders)
        cancer_type = random.choice(cancer_types)
        status = random.choice(statuses)
        
        # Random diagnosis date within last 2 years
        days_ago = random.randint(30, 730)
        diagnosis_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        notes = f"Patient undergoing {status.lower()} protocol. Regular monitoring required."
        
        # Assign to admin user (user_id = 1)
        user_id = 1
        
        patients.append((user_id, name, age, gender, cancer_type, status, diagnosis_date, notes))
    
    # Insert all patients
    cursor.executemany('''
        INSERT INTO patients (user_id, name, age, gender, cancer_type, status, diagnosis_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', patients)
    
    conn.commit()
    conn.close()
    
    print(f"Successfully added 20 patient records to the database!")
    print(f"Total patients now in database: {len(patients)}")
    
    return len(patients)

if __name__ == '__main__':
    add_sample_patients()
