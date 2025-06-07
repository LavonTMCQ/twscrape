source venv/bin/activate && python3 twitter_api_server.py
source venv/bin/activate && python twitter_api_server.py




# Twitter API Server Documentation

This document provides instructions on how to set up and use the Twitter API Server, which allows you to fetch tweets from Twitter accounts using the twscrape package.

## Overview

The Twitter API Server provides a simple HTTP API that your agent can call to fetch tweets from specific Twitter accounts. It uses the twscrape package with Twitter cookies for authentication to avoid rate limits.

## Setup Instructions

### 1. Install Dependencies

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install twscrape fastapi uvicorn requests python-dotenv
```

### 2. Configure Twitter Cookies

1. Create a file named `cookie_string.txt` with your Twitter cookies in the following format:
   ```
   auth_token=YOUR_AUTH_TOKEN; ct0=YOUR_CT0_TOKEN; twid=YOUR_TWID
   ```

2. Make sure the cookies are valid and from an active Twitter session.

### 3. Start the API Server

```bash
# Start the server
python twitter_api_server.py
```

The server will run on http://localhost:8000 by default.

## API Endpoints

### 1. Get User Tweets

**Endpoint:** `/api/user_tweets/{username}`

**Method:** GET

**Parameters:**
- `username` (path parameter): Twitter username without the @ symbol
- `limit` (query parameter): Number of tweets to return (default: 5, max: 100)

**Example Request:**
```
GET http://localhost:8000/api/user_tweets/cashcoldgame?limit=5
```

**Example Response:**
```json
{
  "username": "cashcoldgame",
  "user_id": "1234567890",
  "tweets": [
    {
      "id": "1234567890123456789",
      "url": "https://x.com/cashcoldgame/status/1234567890123456789",
      "date": "2023-06-01T12:34:56+00:00",
      "content": "Tweet content here...",
      "user": {
        "username": "cashcoldgame",
        "displayname": "Cash Cold",
        "verified": false,
        "followers_count": 1000
      },
      "metrics": {
        "replies": 10,
        "retweets": 5,
        "likes": 20,
        "quotes": 2,
        "views": 500
      },
      "media": {
        "photos": [
          {"url": "https://pbs.twimg.com/media/image1.jpg"}
        ],
        "videos": []
      }
    },
    // More tweets...
  ],
  "timestamp": "2023-06-01T12:45:00+00:00"
}
```

### 2. Check API Status

**Endpoint:** `/api/status`

**Method:** GET

**Example Request:**
```
GET http://localhost:8000/api/status
```

**Example Response:**
```json
{
  "status": "ok",
  "accounts": [
    {
      "username": "nuinui3478",
      "active": true,
      "last_used": "2023-06-01T12:34:56+00:00",
      "error_msg": null
    }
  ],
  "timestamp": "2023-06-01T12:45:00+00:00"
}
```

## Using the API Client

A Python client is provided to easily interact with the API:

```python
# Import the client
from twitter_api_client import get_user_tweets

# Get tweets from a user
tweets_data = get_user_tweets("cashcoldgame", limit=5)

# Process the data
for tweet in tweets_data["tweets"]:
    print(f"Tweet: {tweet['content']}")
    print(f"Likes: {tweet['metrics']['likes']}")
```

You can also use the client from the command line:

```bash
# Get tweets from a user
python twitter_api_client.py cashcoldgame 5

# Save tweets to a JSON file
python twitter_api_client.py cashcoldgame 5 --save
```

## Integration with Agents

To integrate this API with your agent:

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

# Example usage in your agent
def agent_function():
    # Get tweets about a stock ticker by searching a financial account
    twitter_data = get_twitter_data("cashcoldgame", limit=5)
    
    # Process the tweets
    for tweet in twitter_data["tweets"]:
        # Analyze the tweet content
        print(f"Analyzing tweet: {tweet['content']}")
        
        # Your agent's analysis logic here
        # ...
```

## Important Notes

1. **Rate Limits**: Twitter has rate limits on API calls. The server will handle these limits, but you may need to wait if you hit them.

2. **Cookie Expiration**: Twitter cookies expire periodically. If the API stops working, you may need to update the cookies in `cookie_string.txt`.

3. **Error Handling**: The API will return appropriate HTTP status codes and error messages if something goes wrong.

4. **Search Limitations**: The search endpoint is more strictly rate-limited by Twitter. The user_tweets endpoint is more reliable.

## Troubleshooting

1. **API Returns 500 Error**: Check if your cookies are valid and not expired.

2. **No Tweets Returned**: The account might not have any tweets, or you might be rate-limited.

3. **Server Won't Start**: Make sure all dependencies are installed and the cookie file exists.

4. **Rate Limit Errors**: Wait for the rate limit to reset (usually 15 minutes) or add more accounts to the pool.

## Files Included

1. `twitter_api_server.py` - The main API server
2. `twitter_api_client.py` - Client for interacting with the API
3. `cookie_string.txt` - File containing Twitter cookies

## Maintenance

To keep the API running smoothly:

1. Periodically update the cookies in `cookie_string.txt`
2. Monitor the API status endpoint to check account health
3. Consider adding multiple Twitter accounts to increase rate limits
