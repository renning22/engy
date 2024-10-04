
#!/bin/bash

# Create and activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install required libraries
pip install flask flask-socketio flask-cors
pip install /data/finae/engy

# Start the server
python server.py
