
#!/bin/bash

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required libraries
pip install Flask Flask-CORS crewai langchain-anthropic langchain-community requests beautifulsoup4 duckduckgo-search

# Start the server
python server.py
