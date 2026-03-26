import os, random, string
from datetime import datetime
import pandas as pd

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def format_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %b %Y')
    except:
        return date_str

def export_to_csv(data, filename):
    path = os.path.join('exports', filename)
    os.makedirs('exports', exist_ok=True)
    pd.DataFrame(data).to_csv(path, index=False)
    return path

def export_to_excel(data, filename):
    path = os.path.join('exports', filename)
    os.makedirs('exports', exist_ok=True)
    pd.DataFrame(data).to_excel(path, index=False)
    return path

def export_to_pdf(data, filename, title='Report'):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    os.makedirs('exports', exist_ok=True)
    path = os.path.join('exports', filename)
    c = canvas.Canvas(path, pagesize=letter)
    c.drawString(100, 750, title)
    c.save()
    return path
