
#!/bin/bash

# Update pip
pip install --upgrade pip

# Install required libraries
pip install Flask flask-cors crewai langchain_anthropic markdown

export ANTHROPIC_API_KEY='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'

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable is not set."
    echo "Please set it by running: export ANTHROPIC_API_KEY=your_api_key_here"
    exit 1
fi

# Start the server
python server.py
