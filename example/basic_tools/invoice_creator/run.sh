
#!/bin/sh

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask Flask-CORS Pillow reportlab pdf2image

# Start the server
python server.py
