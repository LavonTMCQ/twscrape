import asyncio
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from twscrape import API, gather
from twscrape.logger import set_log_level

# Load environment variables
load_dotenv()

# Configure logging
set_log_level("INFO")

# Initialize FastAPI app
app = FastAPI(
    title="Twitter Scraper API",
    description="API for scraping Twitter data for stock tickers",
    version="1.0.0",
)

# Initialize Twitter API client
twitter_api = API()

# Models for API responses
class TweetData(BaseModel):
    id: str
    url: str
    date: str
    content: str
    user: Dict[str, Any]
    metrics: Dict[str, int]

class TickerResponse(BaseModel):
    ticker: str
    query: str
    tweets: List[TweetData]
    sentiment: Optional[Dict[str, Any]] = None
    timestamp: str

# Initialize Twitter API with account credentials
@app.on_event("startup")
async def startup_event():
    # Get credentials from environment variables
    username = os.getenv("TWITTER_USERNAME")
    password = os.getenv("TWITTER_PASSWORD")
    email = os.getenv("TWITTER_EMAIL")
    email_password = os.getenv("TWITTER_EMAIL_PASSWORD")
    proxy = os.getenv("TWITTER_PROXY")

    # Check if we have a cookies file
    cookies_file = os.getenv("TWITTER_COOKIES_FILE", "twitter_cookies.json")
    cookies = None

    if os.path.exists(cookies_file):
        try:
            with open(cookies_file, 'r') as f:
                cookies = json.load(f)
            print(f"Loaded cookies from {cookies_file}")
        except Exception as e:
            print(f"Error loading cookies file: {e}")

    if not username:
        raise Exception("Twitter username not configured. Check your .env file.")

    # Add account to the pool
    try:
        await twitter_api.pool.add_account(
            username=username,
            password=password or "",
            email=email or "",
            email_password=email_password or "",
            proxy=proxy,
            cookies=cookies
        )

        # Check if we have active accounts
        accounts_info = await twitter_api.pool.accounts_info()
        has_active = any(account.get('active', False) for account in accounts_info)

        if not has_active:
            print("No active accounts found. Trying to login...")
            # Try to login if we don't have active accounts
            try:
                await twitter_api.pool.login_all()
                print("Login successful!")
            except Exception as e:
                print(f"Error logging in: {e}")
                print("If you're having login issues, try using browser cookies.")
                print("See COOKIE_EXTRACTION_GUIDE.md for instructions.")
        else:
            print("Active account found with cookies!")

    except Exception as e:
        print(f"Error setting up Twitter API: {e}")
        print("The API will start, but Twitter functionality may not work.")

@app.get("/")
async def root():
    return {"message": "Twitter Scraper API is running"}

@app.get("/api/search/{ticker}", response_model=TickerResponse)
async def search_ticker(
    ticker: str,
    limit: int = Query(5, ge=1, le=100, description="Number of tweets to return"),
    product: str = Query("Top", description="Search tab: Top, Latest, or Media")
):
    """
    Search for tweets related to a stock ticker and return the top results.

    - **ticker**: Stock ticker symbol (e.g., AAPL, TSLA)
    - **limit**: Number of tweets to return (default: 5)
    - **product**: Search tab to use (default: Top)
    """
    # Format the query to search for the ticker symbol
    # The $ sign is important for stock tickers on Twitter
    query = f"${ticker.upper()}"

    try:
        # Search for tweets
        tweets = await gather(twitter_api.search(
            query,
            limit=limit,
            kv={"product": product}
        ))

        # Process tweets
        processed_tweets = []
        for tweet in tweets:
            processed_tweets.append(TweetData(
                id=tweet.id_str,
                url=tweet.url,
                date=tweet.date.isoformat(),
                content=tweet.rawContent,
                user={
                    "username": tweet.user.username,
                    "displayname": tweet.user.displayname,
                    "verified": tweet.user.verified or False,
                    "blue": tweet.user.blue or False,
                    "followers_count": tweet.user.followersCount,
                },
                metrics={
                    "replies": tweet.replyCount,
                    "retweets": tweet.retweetCount,
                    "likes": tweet.likeCount,
                    "quotes": tweet.quoteCount,
                    "views": tweet.viewCount or 0,
                }
            ))

        # Create response
        response = TickerResponse(
            ticker=ticker.upper(),
            query=query,
            tweets=processed_tweets,
            sentiment=None,  # Could add sentiment analysis here in the future
            timestamp=datetime.now().isoformat()
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching Twitter: {str(e)}")

@app.get("/api/accounts")
async def get_accounts():
    """Get information about the configured Twitter accounts"""
    try:
        accounts_info = await twitter_api.pool.accounts_info()
        return {"accounts": [dict(x) for x in accounts_info]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting accounts: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("twitter_scraper_api:app", host="0.0.0.0", port=8000, reload=True)
