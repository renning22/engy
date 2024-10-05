
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask flask-cors ffmpeg-python

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null
then
    echo "FFmpeg is not installed. Please install FFmpeg and try again."
    exit 1
fi

# Start the server
python server.py
