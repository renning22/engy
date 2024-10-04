
#!/bin/bash


# Install required libraries
pip install flask flask-cors flask-socketio crewai langchain_anthropic langchain_community

# Start the server
python server.py
