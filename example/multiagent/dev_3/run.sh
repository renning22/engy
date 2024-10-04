
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install flask flask-cors flask-socketio crewai python-dotenv langchain langchain-anthropic langchain-community

# Start the server
python server.py
