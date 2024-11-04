
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print with color
echo_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Error handling
set -e

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo_color $RED "Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo_color $BLUE "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo_color $BLUE "Activating virtual environment..."
source venv/bin/activate

# Install or upgrade pip
echo_color $BLUE "Upgrading pip..."
python -m pip install --upgrade pip

# Install required packages
echo_color $BLUE "Installing required packages..."
pip install flask flask-cors

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo_color $RED "Error: server.py not found in current directory!"
    exit 1
fi

# Check if index.html exists
if [ ! -f "index.html" ]; then
    echo_color $RED "Error: index.html not found in current directory!"
    exit 1
fi

# Start the server
echo_color $GREEN "Starting the server..."
echo_color $GREEN "Access the website at http://localhost:8933"
python server.py

# Deactivate virtual environment on script exit
deactivate
