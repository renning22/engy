
#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required libraries
pip install Flask Flask-CORS sympy

# Start the server
python server.py
