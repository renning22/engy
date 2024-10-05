
#!/bin/bash

# Create and activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install required libraries
pip install Flask Flask-CORS Flask-SQLAlchemy Pillow reportlab

# Start the server
python server.py
