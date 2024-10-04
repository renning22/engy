
#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install required libraries
echo "Installing required libraries..."
pip install flask flask-socketio flask-cors /data/finae/finae

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo "Error: server.py not found in the current directory."
    exit 1
fi

# Start the server
echo "Starting the server..."
python server.py
