
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask Flask-CORS paramiko

# Start the server
python server.py
