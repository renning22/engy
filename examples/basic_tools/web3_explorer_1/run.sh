
#!/bin/bash

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate

# Install required libraries
pip install Flask flask-cors web3 python-dotenv

# Start the server
python server.py
