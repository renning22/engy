
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask Flask-CORS Flask-SocketIO Flask-HTTPAuth docker

# Start the server
python server.py
