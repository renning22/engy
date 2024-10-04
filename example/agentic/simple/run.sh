
#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if pip is installed
if ! command_exists pip; then
  echo "Error: pip is not installed. Please install pip and try again."
  exit 1
fi

# Install required libraries
echo "Installing required libraries..."
pip install flask flask-cors anthropic litellm

export ANTHROPIC_API_KEY="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"

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "Error: ANTHROPIC_API_KEY environment variable is not set."
  echo "Please set it by running: export ANTHROPIC_API_KEY=your_api_key_here"
  exit 1
fi

# Start the server
echo "Starting the server..."
python server.py
