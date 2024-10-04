
import os
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import json
import uuid

app = Flask(__name__, static_folder='.')
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Invoice model
class Invoice(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    company_info = db.Column(db.String(500))
    items = db.Column(db.String(1000))
    total = db.Column(db.Float)
    image_path = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'company_info': self.company_info,
            'items': json.loads(self.items),
            'total': self.total,
            'image_path': self.image_path
        }

with app.app_context():
    db.create_all()

def process_image(image_file):
    filename = secure_filename(image_file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image_file.save(filepath)
    
    # Resize and optimize image
    with Image.open(filepath) as img:
        img.thumbnail((800, 800))
        img.save(filepath, optimize=True, quality=85)
    
    return filepath

def generate_invoice(data):
    invoice_id = str(uuid.uuid4())
    company_info = data['company_info']
    items = data['items']
    total = sum(item['price'] * item['quantity'] for item in items)
    image_path = data['image_path']

    invoice = Invoice(
        id=invoice_id,
        company_info=company_info,
        items=json.dumps(items),
        total=total,
        image_path=image_path
    )
    db.session.add(invoice)
    db.session.commit()

    return invoice

def create_pdf(invoice):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add company info
    c.drawString(50, height - 50, f"Company Info: {invoice.company_info}")

    # Add items
    y = height - 100
    for item in json.loads(invoice.items):
        c.drawString(50, y, f"{item['name']} - Quantity: {item['quantity']} - Price: ${item['price']}")
        y -= 20

    # Add total
    c.drawString(50, y - 20, f"Total: ${invoice.total}")

    # Add image
    if invoice.image_path:
        c.drawImage(invoice.image_path, 50, y - 220, width=200, height=200)

    c.save()
    buffer.seek(0)
    return buffer

def create_png(invoice):
    # For simplicity, we'll create a basic image with text
    img = Image.new('RGB', (800, 600), color='white')
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    d.text((10, 10), f"Invoice ID: {invoice.id}", fill=(0, 0, 0))
    d.text((10, 30), f"Company Info: {invoice.company_info}", fill=(0, 0, 0))
    d.text((10, 50), f"Total: ${invoice.total}", fill=(0, 0, 0))

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No image file selected'}), 400
    
    filepath = process_image(image_file)
    return jsonify({'image_path': filepath})

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice_route():
    data = request.json
    invoice = generate_invoice(data)
    return jsonify(invoice.to_dict()), 201

@app.route('/invoices', methods=['GET'])
def get_invoices():
    invoices = Invoice.query.all()
    return jsonify([invoice.to_dict() for invoice in invoices])

@app.route('/invoice/<id>', methods=['GET'])
def get_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    return jsonify(invoice.to_dict())

@app.route('/download/<id>', methods=['GET'])
def download_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    format = request.args.get('format', 'pdf')

    if format == 'pdf':
        buffer = create_pdf(invoice)
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'invoice_{id}.pdf')
    elif format == 'png':
        buffer = create_png(invoice)
        return send_file(buffer, mimetype='image/png', as_attachment=True, download_name=f'invoice_{id}.png')
    else:
        return jsonify({'error': 'Invalid format specified'}), 400

if __name__ == '__main__':
    app.run(host='localhost', port=7527, debug=True)
