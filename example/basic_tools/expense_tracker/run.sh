
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install flask flask-sqlalchemy flask-cors

# Start the server
python server.py
