
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
pip install flask flask_sqlalchemy flask_cors

# Install local library if it exists
if [ -d "/data/finae/finae" ]; then
    echo "Installing local finae library..."
    pip install /data/finae/finae
else
    echo "Local finae library not found, skipping..."
fi

# Start the server
echo "Starting the server..."
python server.py
