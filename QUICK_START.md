# Twitter API Server Quick Start Guide

This guide provides the essential steps to get the Twitter API Server up and running quickly.

## 1. Setup

```bash
# Activate the virtual environment
source venv/bin/activate

# Make sure all dependencies are installed
pip install twscrape fastapi uvicorn requests python-dotenv
```

## 2. Start the Server

```bash
# Start the API server
python twitter_api_server.py
```

The server will be available at http://localhost:8000

## 3. Test the API

### Using the provided client:

```bash
# Get 5 tweets from @cashcoldgame
python twitter_api_client.py cashcoldgame 5
```

### Using curl:

```bash
# Get 5 tweets from @cashcoldgame
curl "http://localhost:8000/api/user_tweets/cashcoldgame?limit=5"

# Check API status
curl "http://localhost:8000/api/status"
```

## 4. Integrate with Your Agent

```python
import requests

def get_twitter_data(username, limit=5):
    """Function for your agent to call the Twitter API"""
    response = requests.get(
        f"http://localhost:8000/api/user_tweets/{username}",
        params={"limit": limit}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to get tweets: {response.text}"}

# Example usage
twitter_data = get_twitter_data("cashcoldgame", 5)
```

## 5. Updating Cookies

If the API stops working, you may need to update your Twitter cookies:

1. Log in to Twitter in your browser
2. Extract the cookies (auth_token, ct0, twid)
3. Update the `cookie_string.txt` file
4. Restart the server

## Need More Help?

See the full documentation in `TWITTER_API_DOCUMENTATION.md`
