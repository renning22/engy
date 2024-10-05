
#!/bin/bash

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install required libraries
pip install Flask flask-cors

# Start the server
python server.py
