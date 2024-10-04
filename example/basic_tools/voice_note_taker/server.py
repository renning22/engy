
import os
import io
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import speech_recognition as sr
from pydub import AudioSegment
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

app = Flask(__name__, static_folder='.')
CORS(app)

# In-memory storage for temporary files
temp_storage = {}

def convert_to_wav(audio_file):
    audio = AudioSegment.from_file(audio_file)
    wav_data = io.BytesIO()
    audio.export(wav_data, format="wav")
    wav_data.seek(0)
    return wav_data

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_content = file.read()
        
        # Store file content in memory
        temp_storage[filename] = file_content
        
        try:
            # Convert audio to WAV format
            wav_data = convert_to_wav(io.BytesIO(file_content))
            
            # Perform transcription
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_data) as source:
                audio = recognizer.record(source)
            
            text = recognizer.recognize_google(audio)
            
            # Remove temporary file from memory
            del temp_storage[filename]
            
            return jsonify({"transcription": text})
        
        except sr.UnknownValueError:
            return jsonify({"error": "Speech recognition could not understand audio"}), 400
        except sr.RequestError as e:
            return jsonify({"error": f"Could not request results from speech recognition service; {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"An error occurred during transcription: {str(e)}"}), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='localhost', port=8057, debug=True)
