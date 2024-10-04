
#!/bin/bash

# Activate Anaconda environment (uncomment if you're using Anaconda)
# source ~/anaconda3/bin/activate

# Install required libraries
pip install flask flask-cors flask-socketio langchain-anthropic langchain-community python-dotenv crewai

# Start the server
python server.py
