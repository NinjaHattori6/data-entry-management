import random
import string
from datetime import datetime, timedelta
from flask import current_app
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def format_date(date_obj):
    """Format date object to readable string"""
    if date_obj:
        return date_obj.strftime('%Y-%m-%d')
    return ''

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if birth_date:
        today = datetime.now().date()
        birth = birth_date.date() if hasattr(birth_date, 'date') else birth_date
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age
    return 0

def export_to_csv(data, filename):
    """Export data to CSV file"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    return filename

def export_to_excel(data, filename):
    """Export data to Excel file"""
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, engine='openpyxl')
    return filename

def export_to_pdf(data, filename, title='Patient Records'):
    """Export data to PDF file"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = styles['Title']
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Table headers
    headers = list(data[0].keys()) if data else []
    table_data = [headers]
    
    # Table rows
    for row in data:
        table_data.append([str(row.get(header, '')) for header in headers])
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    return filename
