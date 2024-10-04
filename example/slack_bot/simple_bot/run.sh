
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask flask-cors slackclient

# Start the server
python server.py
