
from flask import Flask, request, jsonify, send_file
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

# HTML template with complete JavaScript implementation
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People Counter | AI Detection</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#2563eb',
                        secondary: '#475569',
                        danger: '#dc2626',
                    }
                }
            }
        }
    </script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
</head>
<body class="bg-slate-50 min-h-screen">
    <nav class="bg-white shadow-md">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <i class="fas fa-video text-primary text-2xl mr-2"></i>
                    <span class="font-bold text-xl text-gray-800">AI People Counter</span>
                </div>
                <div class="flex items-center">
                    <span class="text-sm text-gray-500">v1.0</span>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-lg shadow-lg overflow-hidden">
            <div class="relative w-full aspect-video bg-black">
                <video id="videoElement" 
                       class="absolute top-0 left-0 w-full h-full object-contain"
                       autoplay playsinline></video>
                <canvas id="overlayCanvas" 
                        class="absolute top-0 left-0 w-full h-full"></canvas>
                
                <div id="cameraStatus" 
                     class="absolute top-4 right-4 flex items-center bg-black/50 rounded-full px-3 py-1">
                    <div class="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
                    <span class="text-white text-sm">Camera Off</span>
                </div>
            </div>

            <div class="p-6 border-t border-gray-100">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="bg-blue-50 rounded-lg p-4">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-blue-600 font-medium">People Detected</p>
                                <h2 class="text-3xl font-bold text-blue-700" id="countDisplay">0</h2>
                            </div>
                            <div class="text-blue-500">
                                <i class="fas fa-users text-3xl"></i>
                            </div>
                        </div>
                    </div>

                    <div class="bg-green-50 rounded-lg p-4">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-green-600 font-medium">FPS</p>
                                <h2 class="text-3xl font-bold text-green-700" id="fpsDisplay">0</h2>
                            </div>
                            <div class="text-green-500">
                                <i class="fas fa-tachometer-alt text-3xl"></i>
                            </div>
                        </div>
                    </div>

                    <div class="bg-purple-50 rounded-lg p-4">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm text-purple-600 font-medium">Status</p>
                                <h2 class="text-xl font-bold text-purple-700" id="statusDisplay">Ready</h2>
                            </div>
                            <div class="text-purple-500">
                                <i class="fas fa-signal text-3xl"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="p-6 bg-gray-50 border-t border-gray-100">
                <div class="flex justify-center space-x-4">
                    <button id="startButton"
                            class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
                        <i class="fas fa-play mr-2"></i>
                        Start Detection
                    </button>
                    <button id="stopButton"
                            disabled
                            class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-danger hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                        <i class="fas fa-stop mr-2"></i>
                        Stop
                    </button>
                </div>
            </div>
        </div>

        <footer class="mt-8 text-center text-gray-500 text-sm">
            <p>© 2024 AI People Counter. All rights reserved.</p>
        </footer>
    </main>

    <script>
        class CameraManager {
            constructor(videoElement) {
                this.videoElement = videoElement;
                this.stream = null;
            }

            async initialize() {
                try {
                    this.stream = await navigator.mediaDevices.getUserMedia({ 
                        video: { 
                            width: { ideal: 1280 },
                            height: { ideal: 720 }
                        }
                    });
                    this.videoElement.srcObject = this.stream;
                    return true;
                } catch (error) {
                    console.error('Error accessing camera:', error);
                    return false;
                }
            }

            stop() {
                if (this.stream) {
                    this.stream.getTracks().forEach(track => track.stop());
                    this.stream = null;
                }
                this.videoElement.srcObject = null;
            }
        }

        class FrameProcessor {
            constructor(videoElement, canvasElement) {
                this.videoElement = videoElement;
                this.canvas = canvasElement;
                this.ctx = canvasElement.getContext('2d');
            }

            captureFrame() {
                this.canvas.width = this.videoElement.videoWidth;
                this.canvas.height = this.videoElement.videoHeight;
                this.ctx.drawImage(this.videoElement, 0, 0);
                return this.canvas.toDataURL('image/jpeg', 0.8);
            }

            async processFrame() {
                const imageData = this.captureFrame();
                
                try {
                    const response = await fetch('/process_frame', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ image: imageData })
                    });

                    if (!response.ok) throw new Error('Network response was not ok');
                    
                    const result = await response.json();
                    return result;
                } catch (error) {
                    console.error('Error processing frame:', error);
                    return null;
                }
            }

            drawBoxes(boxes) {
                this.ctx.strokeStyle = '#00ff00';
                this.ctx.lineWidth = 2;
                
                boxes.forEach(box => {
                    this.ctx.strokeRect(box.x, box.y, box.width, box.height);
                });
            }
        }

        class PeopleCounterApp {
            constructor() {
                this.videoElement = document.getElementById('videoElement');
                this.canvasElement = document.getElementById('overlayCanvas');
                this.countDisplay = document.getElementById('countDisplay');
                this.startButton = document.getElementById('startButton');
                this.stopButton = document.getElementById('stopButton');
                this.fpsDisplay = document.getElementById('fpsDisplay');
                this.statusDisplay = document.getElementById('statusDisplay');
                this.cameraStatus = document.getElementById('cameraStatus');
                
                this.cameraManager = new CameraManager(this.videoElement);
                this.frameProcessor = new FrameProcessor(this.videoElement, this.canvasElement);
                
                this.processingInterval = null;
                this.lastFrameTime = 0;
                this.setupEventListeners();
            }

            setupEventListeners() {
                this.startButton.addEventListener('click', () => this.start());
                this.stopButton.addEventListener('click', () => this.stop());
            }

            updateCameraStatus(isActive) {
                const indicator = this.cameraStatus.querySelector('div');
                const text = this.cameraStatus.querySelector('span');
                
                if (isActive) {
                    indicator.classList.remove('bg-red-500');
                    indicator.classList.add('bg-green-500');
                    text.textContent = 'Camera Active';
                } else {
                    indicator.classList.remove('bg-green-500');
                    indicator.classList.add('bg-red-500');
                    text.textContent = 'Camera Off';
                }
            }

            updateFPS() {
                const now = performance.now();
                const delta = now - this.lastFrameTime;
                this.lastFrameTime = now;
                const fps = Math.round(1000 / delta);
                this.fpsDisplay.textContent = fps;
            }

            async start() {
                this.statusDisplay.textContent = 'Initializing...';
                const success = await this.cameraManager.initialize();
                if (!success) {
                    this.statusDisplay.textContent = 'Camera Error';
                    alert('Failed to access camera. Please ensure you have granted camera permissions.');
                    return;
                }

                this.startButton.disabled = true;
                this.stopButton.disabled = false;
                this.updateCameraStatus(true);
                this.statusDisplay.textContent = 'Running';

                await new Promise(resolve => {
                    this.videoElement.onloadedmetadata = resolve;
                });

                this.processingInterval = setInterval(async () => {
                    const result = await this.frameProcessor.processFrame();
                    if (result) {
                        this.countDisplay.textContent = result.person_count;
                        this.frameProcessor.drawBoxes(result.boxes);
                        this.updateFPS();
                    }
                }, 100);
            }

            stop() {
                clearInterval(this.processingInterval);
                this.cameraManager.stop();
                this.startButton.disabled = false;
                this.stopButton.disabled = true;
                this.countDisplay.textContent = '0';
                this.fpsDisplay.textContent = '0';
                this.statusDisplay.textContent = 'Ready';
                this.updateCameraStatus(false);
                
                const ctx = this.canvasElement.getContext('2d');
                ctx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            const app = new PeopleCounterApp();
        });
    </script>
</body>
</html>
'''

class PersonDetector:
    def __init__(self):
        self.pose_detector = mp.solutions.pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def detect(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose_detector.process(frame_rgb)
        
        person_count = 0
        boxes = []
        
        if results.pose_landmarks:
            height, width = frame.shape[:2]
            person_count = 1
            
            landmarks = results.pose_landmarks.landmark
            x_coordinates = [landmark.x for landmark in landmarks]
            y_coordinates = [landmark.y for landmark in landmarks]
            
            x_min = int(min(x_coordinates) * width)
            x_max = int(max(x_coordinates) * width)
            y_min = int(min(y_coordinates) * height)
            y_max = int(max(y_coordinates) * height)
            
            boxes.append({
                'x': x_min,
                'y': y_min,
                'width': x_max - x_min,
                'height': y_max - y_min
            })
        
        return person_count, boxes

detector = PersonDetector()

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        image_data = request.json.get('image')
        if not image_data:
            return jsonify({'error': 'No image data received'}), 400
        
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        count, boxes = detector.detect(opencv_image)
        
        return jsonify({
            'person_count': count,
            'boxes': boxes
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"Server running at http://0.0.0.0:5517")
    app.run(host='0.0.0.0', port=5517, debug=True)
