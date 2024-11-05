
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import mediapipe as mp
import base64
import io
from PIL import Image
import os

app = Flask(__name__)
CORS(app)

# Get the directory where server.py is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class PersonDetector:
    def __init__(self):
        # Initialize mediapipe pose detection with good defaults for webcam usage
        self.pose_detector = mp.solutions.pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def detect(self, frame):
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame and detect poses
        results = self.pose_detector.process(frame_rgb)
        
        person_count = 0
        boxes = []
        
        if results.pose_landmarks:
            height, width = frame.shape[:2]
            
            # Count each detected pose as a person
            person_count = 1  # Each result is one person
            
            # Calculate bounding box for the person
            landmarks = results.pose_landmarks.landmark
            x_coordinates = [landmark.x for landmark in landmarks]
            y_coordinates = [landmark.y for landmark in landmarks]
            
            # Convert normalized coordinates to pixel coordinates
            x_min = int(min(x_coordinates) * width)
            x_max = int(max(x_coordinates) * width)
            y_min = int(min(y_coordinates) * height)
            y_max = int(max(y_coordinates) * height)
            
            # Add bounding box coordinates
            boxes.append({
                'x': x_min,
                'y': y_min,
                'width': x_max - x_min,
                'height': y_max - y_min
            })
        
        return person_count, boxes

# Create a global instance of PersonDetector
detector = PersonDetector()

@app.route('/')
def index():
    # Serve the index.html file from the same directory as server.py
    return send_file(os.path.join(CURRENT_DIR, 'index.html'))

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        # Get the image data from the request
        image_data = request.json.get('image')
        if not image_data:
            return jsonify({'error': 'No image data received'}), 400
        
        # Remove the data URL prefix if present
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL Image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Process the frame
        count, boxes = detector.detect(opencv_image)
        
        # Return the results
        return jsonify({
            'person_count': count,
            'boxes': boxes
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handling for missing files
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

if __name__ == '__main__':
    # Check if index.html exists
    if not os.path.exists(os.path.join(CURRENT_DIR, 'index.html')):
        print("Warning: index.html not found in the same directory as server.py")
        print(f"Please ensure index.html is placed in: {CURRENT_DIR}")
    
    print(f"Server running at http://0.0.0.0:5517")
    print(f"Place index.html in: {CURRENT_DIR}")
    app.run(host='0.0.0.0', port=5517, debug=True)
