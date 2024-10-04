
import os
import uuid
import io
from flask import Flask, request, send_file, jsonify, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import threading
import time

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

UPLOAD_FOLDER = 'uploads'
MERGED_FOLDER = 'merged'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(MERGED_FOLDER):
    os.makedirs(MERGED_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MERGED_FOLDER'] = MERGED_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def docx_to_pdf(docx_path, pdf_path):
    doc = Document(docx_path)
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    for para in doc.paragraphs:
        can.drawString(72, 800, para.text)
        can.showPage()
    
    can.save()
    
    packet.seek(0)
    new_pdf = PdfReader(packet)
    
    pdf_writer = PdfWriter()
    for page in new_pdf.pages:
        pdf_writer.add_page(page)
    
    with open(pdf_path, 'wb') as output_file:
        pdf_writer.write(output_file)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400

    pdf_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            if filename.lower().endswith(('.doc', '.docx')):
                pdf_path = os.path.splitext(file_path)[0] + '.pdf'
                docx_to_pdf(file_path, pdf_path)
                os.remove(file_path)
                pdf_files.append(pdf_path)
            else:
                pdf_files.append(file_path)
    
    merged_filename = f"{uuid.uuid4()}.pdf"
    merged_path = os.path.join(app.config['MERGED_FOLDER'], merged_filename)
    
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(merged_path)
    merger.close()
    
    # Clean up original files
    for pdf in pdf_files:
        os.remove(pdf)
    
    return jsonify({'filename': merged_filename}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join(app.config['MERGED_FOLDER'], filename), as_attachment=True)

def cleanup_files():
    while True:
        time.sleep(3600)  # Run every hour
        current_time = time.time()
        for folder in [UPLOAD_FOLDER, MERGED_FOLDER]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    if os.stat(file_path).st_mtime < current_time - 24 * 3600:
                        os.remove(file_path)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    cleanup_thread = threading.Thread(target=cleanup_files)
    cleanup_thread.start()
    app.run(host='localhost', port=8365, debug=True)
