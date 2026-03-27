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
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    os.makedirs('exports', exist_ok=True)
    path = os.path.join('exports', filename)
    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(title, styles['Title']))
    if data:
        headers = list(data[0].keys())
        table_data = [headers] + [[str(row.get(h, '')) for h in headers] for row in data]
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(table)
    doc.build(elements)
    return path