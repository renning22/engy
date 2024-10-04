
#!/bin/bash

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required libraries
pip install Flask Flask-CORS

# Start the server
python server.py
