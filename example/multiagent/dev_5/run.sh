
#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required libraries
echo "Installing required libraries..."
pip install flask flask-socketio flask-cors /data/finae/engy

# Start the server
echo "Starting the server..."
python server.py
