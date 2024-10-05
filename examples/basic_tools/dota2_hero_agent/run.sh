
#!/bin/bash

# Create and activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate


export ANTHROPIC_API_KEY='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'

# Install required libraries
pip install flask flask-cors flask-sqlalchemy crewai langchain_anthropic requests beautifulsoup4

# Start the server
python server.py
