
import os
import sqlite3
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import uuid
import pdf2image

app = Flask(__name__, static_folder='.')
CORS(app)

# Ensure necessary directories exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')
if not os.path.exists('pdfs'):
    os.makedirs('pdfs')
if not os.path.exists('previews'):
    os.makedirs('previews')

# Initialize SQLite database
def get_db_connection():
    conn = sqlite3.connect('invoices.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS invoices
                 (id TEXT PRIMARY KEY, image_path TEXT, items TEXT, total REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if image_file:
        # Generate a unique filename
        filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
        filepath = os.path.join('uploads', filename)
        
        # Save the image
        image = Image.open(image_file)
        image.save(filepath)
        
        return jsonify({'image_id': filename}), 200

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    data = request.json
    image_id = data.get('image_id')
    items = data.get('items', [])
    
    if not image_id or not items:
        return jsonify({'error': 'Missing image_id or items'}), 400
    
    # Calculate total
    total = sum(item['price'] for item in items)
    
    # Generate PDF
    pdf_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = os.path.join('pdfs', pdf_filename)
    create_pdf(pdf_path, items, total, image_id)
    
    # Generate preview
    preview_filename = f"{uuid.uuid4()}.png"
    preview_path = os.path.join('previews', preview_filename)
    create_preview(pdf_path, preview_path)
    
    # Store invoice data in SQLite
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO invoices (id, image_path, items, total) VALUES (?, ?, ?, ?)",
              (pdf_filename, os.path.join('uploads', image_id), str(items), total))
    conn.commit()
    conn.close()
    
    return jsonify({'invoice_id': pdf_filename, 'preview_id': preview_filename}), 200

@app.route('/download_pdf/<invoice_id>', methods=['GET'])
def download_pdf(invoice_id):
    pdf_path = os.path.join('pdfs', invoice_id)
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        return jsonify({'error': 'PDF not found'}), 404

@app.route('/preview_image/<preview_id>', methods=['GET'])
def preview_image(preview_id):
    preview_path = os.path.join('previews', preview_id)
    if os.path.exists(preview_path):
        return send_file(preview_path, mimetype='image/png')
    else:
        return jsonify({'error': 'Preview not found'}), 404

@app.route('/list_invoices', methods=['GET'])
def list_invoices():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, total, created_at FROM invoices ORDER BY created_at DESC")
    invoices = [dict(row) for row in c.fetchall()]
    conn.close()
    
    # Generate preview IDs
    for invoice in invoices:
        invoice['preview_id'] = f"{uuid.uuid4()}.png"
        preview_path = os.path.join('previews', invoice['preview_id'])
        pdf_path = os.path.join('pdfs', invoice['id'])
        create_preview(pdf_path, preview_path)
    
    return jsonify(invoices)

def create_pdf(pdf_path, items, total, image_id):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Add logo
    logo_path = os.path.join('uploads', image_id)
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 50, height - 100, width=100, height=80)
    
    # Add title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(200, height - 50, "Invoice")
    
    # Add items table
    data = [['Item', 'Price']] + [[item['name'], f"${item['price']:.2f}"] for item in items]
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, 50, height - 300)
    
    # Add total
    c.setFont("Helvetica-Bold", 16)
    c.drawString(400, height - 350, f"Total: ${total:.2f}")
    
    c.save()

def create_preview(pdf_path, preview_path):
    images = pdf2image.convert_from_path(pdf_path)
    images[0].save(preview_path, 'PNG')

if __name__ == '__main__':
    app.run(host='localhost', port=6363, debug=True)
