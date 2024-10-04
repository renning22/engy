
#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required libraries
pip install Flask Flask-CORS

# Install local library (assuming it's in /data/engy/engy)
pip install /data/engy/engy

# Start the server
python server.py
