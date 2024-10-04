
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install flask flask-cors flask-socketio crewai langchain openai duckduckgo-search

# Start the server
python server.py
