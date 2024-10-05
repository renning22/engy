
#!/bin/bash

# Ensure we're using Python 3
PYTHON="python3"

# Check if Python 3 is available
if ! command -v $PYTHON &> /dev/null
then
    echo "Python 3 could not be found. Trying 'python' instead."
    PYTHON="python"
fi

# Install required libraries
echo "Installing required libraries..."
$PYTHON -m pip install Flask Flask-CORS

# Start the server
echo "Starting the server..."
$PYTHON server.py
