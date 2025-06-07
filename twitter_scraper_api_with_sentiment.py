import asyncio
import os
import json
import re
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
    title="Twitter Scraper API with Sentiment Analysis",
    description="API for scraping Twitter data for stock tickers with basic sentiment analysis",
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
    sentiment: Dict[str, Any]
    
class TickerResponse(BaseModel):
    ticker: str
    query: str
    tweets: List[TweetData]
    overall_sentiment: Dict[str, Any]
    timestamp: str

# Simple sentiment analysis function
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Perform a very basic sentiment analysis on the text.
    This is a simplified version - in a real application, you would use
    a more sophisticated NLP library or machine learning model.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Define simple positive and negative word lists
    positive_words = [
        'bullish', 'buy', 'long', 'up', 'gain', 'profit', 'growth', 'positive',
        'strong', 'good', 'great', 'excellent', 'amazing', 'win', 'winning',
        'outperform', 'beat', 'exceed', 'success', 'successful', 'rally', 'moon',
        'rocket', 'soar', 'surge', 'jump', 'rise', 'rising', 'higher', 'breakout'
    ]
    
    negative_words = [
        'bearish', 'sell', 'short', 'down', 'loss', 'lose', 'negative', 'weak',
        'bad', 'poor', 'terrible', 'awful', 'fail', 'failing', 'underperform',
        'miss', 'missed', 'decline', 'drop', 'fall', 'falling', 'lower', 'crash',
        'tank', 'sink', 'plunge', 'plummet', 'tumble', 'collapse', 'dump'
    ]
    
    # Count occurrences
    positive_count = sum(1 for word in positive_words if re.search(r'\b' + word + r'\b', text))
    negative_count = sum(1 for word in negative_words if re.search(r'\b' + word + r'\b', text))
    
    # Calculate sentiment score (-1 to 1)
    total = positive_count + negative_count
    if total == 0:
        score = 0
    else:
        score = (positive_count - negative_count) / total
    
    # Determine sentiment label
    if score > 0.2:
        label = "positive"
    elif score < -0.2:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "score": round(score, 2),
        "label": label,
        "positive_words": positive_count,
        "negative_words": negative_count
    }

# Initialize Twitter API with account credentials
@app.on_event("startup")
async def startup_event():
    # Get credentials from environment variables
    username = os.getenv("TWITTER_USERNAME")
    password = os.getenv("TWITTER_PASSWORD")
    email = os.getenv("TWITTER_EMAIL")
    email_password = os.getenv("TWITTER_EMAIL_PASSWORD")
    proxy = os.getenv("TWITTER_PROXY")
    
    if not all([username, password, email, email_password]):
        raise Exception("Twitter credentials not properly configured. Check your .env file.")
    
    # Add account to the pool
    await twitter_api.pool.add_account(
        username, 
        password, 
        email, 
        email_password,
        proxy=proxy
    )
    
    # Try to login
    try:
        await twitter_api.pool.login_all()
    except Exception as e:
        print(f"Error logging in: {e}")
        # Continue anyway, as we might have valid cookies

@app.get("/")
async def root():
    return {"message": "Twitter Scraper API with Sentiment Analysis is running"}

@app.get("/api/search/{ticker}", response_model=TickerResponse)
async def search_ticker(
    ticker: str, 
    limit: int = Query(5, ge=1, le=100, description="Number of tweets to return"),
    product: str = Query("Top", description="Search tab: Top, Latest, or Media")
):
    """
    Search for tweets related to a stock ticker, analyze sentiment, and return the results.
    
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
        
        # Process tweets and analyze sentiment
        processed_tweets = []
        total_sentiment_score = 0
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        
        for tweet in tweets:
            # Analyze sentiment
            sentiment = analyze_sentiment(tweet.rawContent)
            total_sentiment_score += sentiment["score"]
            sentiment_counts[sentiment["label"]] += 1
            
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
                },
                sentiment=sentiment
            ))
        
        # Calculate overall sentiment
        avg_sentiment = total_sentiment_score / len(tweets) if tweets else 0
        
        # Determine overall sentiment label
        if avg_sentiment > 0.2:
            overall_label = "positive"
        elif avg_sentiment < -0.2:
            overall_label = "negative"
        else:
            overall_label = "neutral"
        
        # Create response
        response = TickerResponse(
            ticker=ticker.upper(),
            query=query,
            tweets=processed_tweets,
            overall_sentiment={
                "score": round(avg_sentiment, 2),
                "label": overall_label,
                "distribution": sentiment_counts
            },
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
    uvicorn.run("twitter_scraper_api_with_sentiment:app", host="0.0.0.0", port=8000, reload=True)
