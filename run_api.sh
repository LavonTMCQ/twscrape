#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it from .env.example"
    echo "cp .env.example .env"
    exit 1
fi

# Install dependencies if needed
if ! pip show fastapi > /dev/null 2>&1 || ! pip show twscrape > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Choose which API to run
if [ "$1" == "sentiment" ]; then
    echo "Starting Twitter Scraper API with sentiment analysis..."
    python twitter_scraper_api_with_sentiment.py
else
    echo "Starting basic Twitter Scraper API..."
    python twitter_scraper_api.py
fi
