"""
Generate 50 sample patient records for testing the Cancer Patient Management System
"""
import sqlite3
import random
from datetime import datetime, timedelta

# Sample data for random generation
first_names = ['John', 'Sarah', 'Robert', 'Maria', 'James', 'Jennifer', 'Michael', 'Linda', 'William', 'Patricia',
               'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Karen', 'Charles', 'Nancy',
               'Daniel', 'Lisa', 'Matthew', 'Betty', 'Anthony', 'Helen', 'Mark', 'Sandra', 'Donald', 'Donna',
               'Paul', 'Carol', 'Steven', 'Ruth', 'Andrew', 'Sharon', 'Kenneth', 'Michelle', 'Joshua', 'Laura',
               'Kevin', 'Emily', 'Brian', 'Kimberly', 'George', 'Deborah', 'Edward', 'Dorothy', 'Ronald', 'Amy']

last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
              'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
              'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
              'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
              'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts']

cancer_types = ['Lung Cancer', 'Breast Cancer', 'Prostate Cancer', 'Ovarian Cancer', 'Colon Cancer',
                'Skin Cancer', 'Brain Cancer', 'Liver Cancer', 'Pancreatic Cancer', 'Leukemia',
                'Lymphoma', 'Kidney Cancer', 'Stomach Cancer', 'Bladder Cancer', 'Thyroid Cancer',
                'Bone Cancer', 'Oral Cancer', 'Cervical Cancer', 'Testicular Cancer', 'Esophageal Cancer']

cancer_stages = ['Stage I', 'Stage II', 'Stage III', 'Stage IV']

blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow',
          'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Pimpri', 'Patna', 'Vadodara', 'Ghaziabad']

states = ['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Telangana', 'West Bengal', 'Gujarat', 'Rajasthan', 'Uttar Pradesh',
          'Madhya Pradesh', 'Bihar', 'Andhra Pradesh', 'Kerala', 'Punjab', 'Haryana', 'Odisha']

treatment_types = ['Chemotherapy', 'Radiation Therapy', 'Surgery', 'Immunotherapy', 'Targeted Therapy',
                   'Hormone Therapy', 'Bone Marrow Transplant', 'Combination Therapy', 'Palliative Care']

doctors = ['Dr. Rajesh Sharma', 'Dr. Priya Patel', 'Dr. Amit Kumar', 'Dr. Sunita Gupta', 'Dr. Vikram Singh',
           'Dr. Anjali Desai', 'Dr. Suresh Reddy', 'Dr. Meera Iyer', 'Dr. Arun Nair', 'Dr. Kavita Joshi']

hospitals = ['Apollo Hospital', 'Fortis Healthcare', 'Max Super Speciality', 'AIIMS', 'Tata Memorial',
             'Manipal Hospital', 'Kokilaben Hospital', 'Lilavati Hospital', 'Nanavati Hospital', 'Jaslok Hospital']

current_statuses = ['Active Treatment', 'Recovered', 'Critical', 'Under Observation', 'Remission', 'Terminal']

risk_levels = ['Low', 'Moderate', 'High']

def generate_patient_id(index):
    """Generate patient ID in format ONC-YYYY-XXXX"""
    year = datetime.now().year
    return f"ONC-{year}-{index:04d}"

def generate_phone():
    """Generate Indian phone number"""
    return f"+91-{random.randint(7000000000, 9999999999)}"

def generate_date(start_year=2020, end_year=2026):
    """Generate random date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    days_between = (end - start).days
    random_days = random.randint(0, days_between)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')

def add_sample_patients():
    """Add 50 sample patient records"""
    conn = sqlite3.connect('oncology_system.db')
    cursor = conn.cursor()
    
    # Get existing count to generate IDs
    cursor.execute("SELECT COUNT(*) FROM patients")
    existing_count = cursor.fetchone()[0]
    
    patients = []
    for i in range(50):
        patient_id = generate_patient_id(existing_count + i + 1)
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        age = random.randint(25, 85)
        gender = random.choice(['Male', 'Female', 'Other'])
        
        # 70% chance of having blood group
        blood_group = random.choice(blood_groups) if random.random() > 0.3 else None
        
        contact_number = generate_phone()
        email = f"{first_name.lower()}.{last_name.lower()}@email.com"
        
        city = random.choice(cities)
        state = random.choice(states)
        
        emergency_contact_name = f"{random.choice(first_names)} {last_name}"
        emergency_contact_number = generate_phone()
        
        cancer_type = random.choice(cancer_types)
        cancer_stage = random.choice(cancer_stages)
        
        # 60% chance of having tumor size
        tumor_size = round(random.uniform(0.5, 15.0), 1) if random.random() > 0.4 else None
        
        # 50% chance of metastasis for Stage III and IV
        if cancer_stage in ['Stage III', 'Stage IV']:
            metastasis = random.choice(['Yes', 'No'])
        else:
            metastasis = random.choice(['Yes', 'No']) if random.random() > 0.7 else 'No'
        
        diagnosis_date = generate_date(2020, 2025)
        
        treatment_type = random.choice(treatment_types) if random.random() > 0.2 else None
        treatment_phase = random.choice(['Pre-treatment', 'Active Treatment', 'Post-treatment', 'Maintenance', 'Follow-up'])
        
        # Chemo cycles (only for chemotherapy patients)
        if treatment_type and 'Chemo' in treatment_type:
            chemo_cycles_planned = random.randint(4, 12)
            chemo_cycles_completed = random.randint(0, chemo_cycles_planned)
        else:
            chemo_cycles_planned = None
            chemo_cycles_completed = None
        
        # Radiation sessions
        if treatment_type and 'Radiation' in treatment_type:
            radiation_sessions_planned = random.randint(15, 35)
            radiation_sessions_completed = random.randint(0, radiation_sessions_planned)
        else:
            radiation_sessions_planned = None
            radiation_sessions_completed = None
        
        surgery_status = random.choice(['Not Required', 'Planned', 'Completed', 'In Recovery'])
        doctor_name = random.choice(doctors)
        hospital_name = random.choice(hospitals)
        
        height = round(random.uniform(150, 185), 1)
        weight = round(random.uniform(45, 95), 1)
        
        # Calculate BMI
        height_m = height / 100
        bmi = round(weight / (height_m ** 2), 2)
        
        blood_pressure = f"{random.randint(110, 140)}/{random.randint(70, 90)}"
        heart_rate = random.randint(60, 100)
        
        risk_level = random.choice(risk_levels)
        current_status = random.choice(current_statuses)
        
        # Next appointment within next 3 months
        next_appointment = (datetime.now() + timedelta(days=random.randint(7, 90))).strftime('%Y-%m-%d')
        
        created_by = 1  # Admin user
        
        patients.append((
            patient_id, full_name, age, gender, blood_group, contact_number, email,
            city, state, emergency_contact_name, emergency_contact_number,
            cancer_type, cancer_stage, tumor_size, metastasis, diagnosis_date,
            treatment_type, treatment_phase, chemo_cycles_planned, chemo_cycles_completed,
            radiation_sessions_planned, radiation_sessions_completed, surgery_status,
            doctor_name, hospital_name, height, weight, bmi, blood_pressure, heart_rate,
            risk_level, current_status, next_appointment, created_by
        ))
    
    # Insert all patients
    cursor.executemany("""
        INSERT INTO patients (
            patient_id, full_name, age, gender, blood_group, contact_number, email,
            city, state, emergency_contact_name, emergency_contact_number,
            cancer_type, cancer_stage, tumor_size, metastasis, diagnosis_date,
            treatment_type, treatment_phase, chemo_cycles_planned, chemo_cycles_completed,
            radiation_sessions_planned, radiation_sessions_completed, surgery_status,
            doctor_name, hospital_name, height, weight, bmi, blood_pressure, heart_rate,
            risk_level, current_status, next_appointment, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, patients)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Successfully added 50 patient records to the database!")
    print(f"📊 Patient IDs range from ONC-{datetime.now().year}-{existing_count+1:04d} to ONC-{datetime.now().year}-{existing_count+50:04d}")

if __name__ == '__main__':
    add_sample_patients()
