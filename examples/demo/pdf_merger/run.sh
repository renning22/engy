
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask flask-cors PyPDF2 python-docx reportlab Werkzeug

# Start the server
python server.py
