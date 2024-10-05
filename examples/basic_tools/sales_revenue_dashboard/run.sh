
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask Flask-SQLAlchemy Flask-CORS pandas

# Start the server
python server.py
