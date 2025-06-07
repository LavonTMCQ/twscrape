#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! pip show fastapi > /dev/null 2>&1 || ! pip show twscrape > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install twscrape fastapi uvicorn requests python-dotenv
fi

# Check if cookie file exists
if [ ! -f "cookie_string.txt" ]; then
    echo "Error: cookie_string.txt not found."
    echo "Please run update_cookies.py to create it."
    exit 1
fi

# Start the server
echo "Starting Twitter API Server..."
python twitter_api_server.py
