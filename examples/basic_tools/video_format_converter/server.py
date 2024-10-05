
import os
import time
import uuid
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import ffmpeg
from werkzeug.utils import secure_filename
import threading

app = Flask(__name__, static_folder='.')
CORS(app)

UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

job_status = {}

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        job_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, f"{job_id}_{filename}")
        file.save(file_path)
        job_status[job_id] = 'uploaded'
        return jsonify({'job_id': job_id}), 200

@app.route('/convert', methods=['POST'])
def convert_video():
    data = request.json
    job_id = data.get('job_id')
    speed = data.get('speed', 1.0)
    resolution = data.get('resolution', '720p')

    if job_id not in job_status:
        return jsonify({'error': 'Invalid job ID'}), 400

    input_file = next((f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(job_id)), None)
    if not input_file:
        return jsonify({'error': 'Input file not found'}), 404

    input_path = os.path.join(UPLOAD_FOLDER, input_file)
    output_filename = f"{job_id}_converted.mp4"
    output_path = os.path.join(CONVERTED_FOLDER, output_filename)

    job_status[job_id] = 'processing'

    def process_video():
        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'setpts', f'{1/speed}*PTS')
            if resolution == '720p':
                stream = ffmpeg.filter(stream, 'scale', 1280, 720)
            elif resolution == '1080p':
                stream = ffmpeg.filter(stream, 'scale', 1920, 1080)
            elif resolution == '480p':
                stream = ffmpeg.filter(stream, 'scale', 854, 480)
            elif resolution == '360p':
                stream = ffmpeg.filter(stream, 'scale', 640, 360)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream)
            job_status[job_id] = 'completed'
        except Exception as e:
            print(f"Error processing video: {str(e)}")
            job_status[job_id] = 'failed'

    threading.Thread(target=process_video).start()

    return jsonify({'message': 'Conversion started', 'job_id': job_id}), 202

@app.route('/download/<job_id>', methods=['GET'])
def download_file(job_id):
    if job_id not in job_status or job_status[job_id] != 'completed':
        return jsonify({'error': 'File not ready or does not exist'}), 404

    output_filename = f"{job_id}_converted.mp4"
    output_path = os.path.join(CONVERTED_FOLDER, output_filename)

    if not os.path.exists(output_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(output_path, as_attachment=True)

@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    if job_id not in job_status:
        return jsonify({'error': 'Invalid job ID'}), 404
    return jsonify({'status': job_status[job_id]}), 200

def cleanup_old_files():
    while True:
        time.sleep(3600)  # Run every hour
        current_time = time.time()
        for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    if os.stat(file_path).st_mtime < current_time - 86400:  # 24 hours
                        os.remove(file_path)

if __name__ == '__main__':
    threading.Thread(target=cleanup_old_files, daemon=True).start()
    app.run(host='localhost', port=8667)
