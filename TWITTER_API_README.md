# Twitter Scraper API

A local API endpoint that scrapes Twitter for stock ticker information using the `twscrape` package.

## Features

- Search for tweets related to stock tickers
- Get the top tweets for a given ticker symbol
- Configure the number of tweets to return
- Choose between different search tabs (Top, Latest, Media)

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Twitter account credentials:

```bash
cp .env.example .env
```

Then edit the `.env` file with your actual Twitter credentials.

## Usage

1. Start the API server:

```bash
python twitter_scraper_api.py
```

2. The API will be available at `http://localhost:8000`

3. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

### GET /api/search/{ticker}

Search for tweets related to a stock ticker.

**Parameters:**
- `ticker`: Stock ticker symbol (e.g., AAPL, TSLA)
- `limit`: Number of tweets to return (default: 5)
- `product`: Search tab to use (default: Top)

**Example:**
```
GET /api/search/AAPL?limit=5&product=Top
```

**Response:**
```json
{
  "ticker": "AAPL",
  "query": "$AAPL",
  "tweets": [
    {
      "id": "1234567890",
      "url": "https://x.com/username/status/1234567890",
      "date": "2023-06-01T12:34:56+00:00",
      "content": "Just bought more $AAPL shares! Bullish on their new product lineup.",
      "user": {
        "username": "investor123",
        "displayname": "Stock Investor",
        "verified": true,
        "blue": true,
        "followers_count": 5000
      },
      "metrics": {
        "replies": 10,
        "retweets": 25,
        "likes": 100,
        "quotes": 5,
        "views": 1000
      }
    },
    // More tweets...
  ],
  "timestamp": "2023-06-01T12:45:00+00:00"
}
```

### GET /api/accounts

Get information about the configured Twitter accounts.

## Integration with Agents

To integrate this API with your agent:

1. Have your agent make HTTP requests to the API endpoint
2. Parse the JSON response to extract tweet data
3. Use the tweet content for sentiment analysis or other processing

Example agent code:
```python
import requests

def get_ticker_tweets(ticker, limit=5):
    response = requests.get(f"http://localhost:8000/api/search/{ticker}?limit={limit}")
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to get tweets: {response.text}"}
```

## Notes

- This API requires valid Twitter credentials to work
- Twitter has rate limits, so excessive usage may result in temporary blocks
- For best results, use multiple Twitter accounts and proxies

## License

MIT
