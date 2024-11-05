
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AI People Counter Setup...${NC}"

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install required packages
echo -e "${YELLOW}Installing required packages...${NC}"
pip install flask \
    flask-cors \
    opencv-python \
    mediapipe \
    numpy \
    pillow

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install required packages.${NC}"
    deactivate
    exit 1
fi

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo -e "${RED}server.py not found in current directory.${NC}"
    deactivate
    exit 1
fi

# Check if index.html exists
if [ ! -f "index.html" ]; then
    echo -e "${RED}index.html not found in current directory.${NC}"
    deactivate
    exit 1
fi

# Start the server
echo -e "${GREEN}Starting the server...${NC}"
echo -e "${YELLOW}Access the application at http://localhost:5517${NC}"
python server.py

# Deactivate virtual environment when the server stops
deactivate
