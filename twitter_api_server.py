import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from twscrape import API, gather

# Initialize FastAPI app
app = FastAPI(
    title="Twitter API Server",
    description="API for fetching tweets from Twitter accounts",
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
    media: Optional[Dict[str, Any]] = None

class UserTweetsResponse(BaseModel):
    username: str
    user_id: str
    tweets: List[TweetData]
    timestamp: str

# Initialize Twitter API with cookies on startup
@app.on_event("startup")
async def startup_event():
    # Load cookie string
    cookie_file = "cookie_string.txt"
    
    if not os.path.exists(cookie_file):
        raise Exception(f"Cookie file {cookie_file} not found")
    
    with open(cookie_file, "r") as f:
        cookie_string = f.read().strip()
    
    # Add account with cookie string
    username = "nuinui3478"  # Your Twitter username
    
    # Add the account
    await twitter_api.pool.add_account(
        username=username,
        password="",  # Not needed with cookies
        email="",     # Not needed with cookies
        email_password="",  # Not needed with cookies
        cookies=cookie_string
    )
    
    # Check if account is active
    accounts_info = await twitter_api.pool.accounts_info()
    has_active = any(dict(account).get('active', False) for account in accounts_info)
    
    if not has_active:
        print("Warning: No active Twitter accounts found. API may not work correctly.")
    else:
        print("Twitter API initialized successfully with active account.")

@app.get("/")
async def root():
    return {"message": "Twitter API Server is running"}

@app.get("/api/user_tweets/{username}", response_model=UserTweetsResponse)
async def get_user_tweets(
    username: str, 
    limit: int = Query(5, ge=1, le=100, description="Number of tweets to return")
):
    """
    Get tweets from a specific Twitter user.
    
    - **username**: Twitter username (without the @ symbol)
    - **limit**: Number of tweets to return (default: 5, max: 100)
    """
    try:
        # First, get the user profile
        user = await twitter_api.user_by_login(username)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User @{username} not found")
        
        # Get the user's tweets
        tweets = await gather(twitter_api.user_tweets(user.id, limit=limit))
        
        # Process tweets
        processed_tweets = []
        for tweet in tweets:
            # Process media
            media_info = None
            if tweet.media:
                media_info = {
                    "photos": [{"url": photo.url} for photo in tweet.media.photos] if tweet.media.photos else [],
                    "videos": [{"url": sorted(video.variants, key=lambda x: x.bitrate)[-1].url} 
                              for video in tweet.media.videos] if tweet.media.videos else []
                }
            
            processed_tweets.append(TweetData(
                id=tweet.id_str,
                url=tweet.url,
                date=tweet.date.isoformat(),
                content=tweet.rawContent,
                user={
                    "username": tweet.user.username,
                    "displayname": tweet.user.displayname,
                    "verified": tweet.user.verified or False,
                    "followers_count": tweet.user.followersCount,
                },
                metrics={
                    "replies": tweet.replyCount,
                    "retweets": tweet.retweetCount,
                    "likes": tweet.likeCount,
                    "quotes": tweet.quoteCount,
                    "views": tweet.viewCount or 0,
                },
                media=media_info
            ))
        
        # Create response
        response = UserTweetsResponse(
            username=user.username,
            user_id=str(user.id),
            tweets=processed_tweets,
            timestamp=datetime.now().isoformat()
        )
        
        return response
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tweets: {str(e)}")

@app.get("/api/status")
async def get_status():
    """Get information about the Twitter API status"""
    try:
        accounts_info = await twitter_api.pool.accounts_info()
        return {
            "status": "ok",
            "accounts": [dict(x) for x in accounts_info],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("twitter_api_server:app", host="0.0.0.0", port=8000, reload=True)
