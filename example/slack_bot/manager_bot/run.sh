
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install flask flask-cors slack_sdk apscheduler

# Start the server
python server.py
