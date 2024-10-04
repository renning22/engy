
#!/bin/bash

# Ensure we're using Python 3
PYTHON_CMD="python3"

# Check if Python 3 is available
if ! command -v $PYTHON_CMD &> /dev/null
then
    echo "Python 3 could not be found. Trying 'python' command..."
    PYTHON_CMD="python"
fi

# Install required libraries
echo "Installing required libraries..."
$PYTHON_CMD -m pip install Flask flask-cors web3

# Start the server
echo "Starting the server..."
$PYTHON_CMD server.py
