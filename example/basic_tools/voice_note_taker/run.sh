
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask flask-cors SpeechRecognition pydub

# Install FFmpeg (required by pydub)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y ffmpeg
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install ffmpeg
else
    echo "Please install FFmpeg manually for your operating system"
fi

# Start the server
python server.py
