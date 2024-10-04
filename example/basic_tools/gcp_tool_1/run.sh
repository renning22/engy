
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask flask-cors google-auth google-auth-httplib2 google-api-python-client

# Start the server
python server.py
