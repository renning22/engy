
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask flask-cors requests pandas plotly dash

# Start the server
python server.py
