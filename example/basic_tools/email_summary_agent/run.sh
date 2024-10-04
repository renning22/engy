
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask flask-cors google-auth google-auth-oauthlib google-api-python-client crewai langchain openai

# Start the server
python server.py
