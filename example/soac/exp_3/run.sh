
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
pip install Flask flask-cors flask-socketio

# Install local library if it exists
if [ -d "/data/engy/engy" ]; then
    echo "Installing local engy library..."
    pip install /data/engy/engy
else
    echo "Local engy library not found. Skipping..."
fi

# Start the server
echo "Starting the server..."
python server.py

# Keep the script running
while true; do
    echo "Server is running. Press Ctrl+C to stop."
    sleep 60
done
