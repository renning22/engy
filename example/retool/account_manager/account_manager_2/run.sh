
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

# Install required packages
echo "Installing required packages..."
pip install Flask Flask-SQLAlchemy Flask-CORS marshmallow

# Check if /data/finae/engy exists and install it if it does
if [ -d "/data/finae/engy" ]; then
    echo "Installing local finae package..."
    pip install /data/finae/engy
fi

# Run the server
echo "Starting the server..."
python server.py
