
#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required libraries
echo "Installing required libraries..."
pip install Flask flask-cors flask-socketio

# Start the server
echo "Starting the Web Search & Scraper Agent server..."
python server.py

# Keep the script running
while true; do
    echo "Web Search & Scraper Agent server is running on port 8593. Press Ctrl+C to stop."
    sleep 60
done
