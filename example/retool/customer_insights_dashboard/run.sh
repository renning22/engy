
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
pip install Flask Flask-SQLAlchemy Flask-CORS Werkzeug Flask-HTTPAuth SQLAlchemy-FullText-Search

# Check if the local library exists and install it
if [ -d "/data/engy/engy" ]; then
    echo "Installing local library..."
    pip install /data/engy/engy
else
    echo "Local library not found at /data/engy/engy. Skipping..."
fi

# Start the server
echo "Starting the server..."
python server.py
