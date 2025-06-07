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
    title="Twitter API Server - Railway Hosted",
    description="API for fetching tweets from Twitter accounts - Hosted on Railway",
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

class SearchResponse(BaseModel):
    query: str
    tweets: List[TweetData]
    timestamp: str

# Initialize Twitter API with cookies on startup
@app.on_event("startup")
async def startup_event():
    # Try to load cookie string from environment variable first
    cookie_string = os.getenv("TWITTER_COOKIE_STRING")
    
    if not cookie_string:
        # Fallback to file if environment variable not set
        cookie_file = "cookie_string.txt"
        if os.path.exists(cookie_file):
            with open(cookie_file, "r") as f:
                cookie_string = f.read().strip()
    
    if not cookie_string:
        print("Warning: No Twitter cookies found. API may not work correctly.")
        return
    
    # Add account with cookie string
    username = os.getenv("TWITTER_USERNAME", "nuinui3478")
    
    try:
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
    except Exception as e:
        print(f"Error initializing Twitter API: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Twitter API Server is running on Railway",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    try:
        accounts_info = await twitter_api.pool.accounts_info()
        has_active = any(dict(account).get('active', False) for account in accounts_info)
        
        return {
            "status": "healthy" if has_active else "degraded",
            "active_accounts": has_active,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

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
                id=str(tweet.id),
                url=tweet.url,
                date=tweet.date.isoformat(),
                content=tweet.rawContent,
                user={
                    "username": tweet.user.username,
                    "displayName": tweet.user.displayname,
                    "id": str(tweet.user.id),
                    "verified": tweet.user.verified,
                    "followersCount": tweet.user.followersCount,
                    "followingCount": tweet.user.followingCount,
                },
                metrics={
                    "retweets": tweet.retweetCount,
                    "likes": tweet.likeCount,
                    "replies": tweet.replyCount,
                    "quotes": tweet.quoteCount,
                    "bookmarks": tweet.bookmarkCount,
                    "views": tweet.viewCount or 0,
                },
                media=media_info
            ))
        
        return UserTweetsResponse(
            username=username,
            user_id=str(user.id),
            tweets=processed_tweets,
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tweets: {str(e)}")

@app.get("/api/search/{query}", response_model=SearchResponse)
async def search_tweets(
    query: str,
    limit: int = Query(10, ge=1, le=100, description="Number of tweets to return")
):
    """
    Search for tweets with a specific query.
    
    - **query**: Search query
    - **limit**: Number of tweets to return (default: 10, max: 100)
    """
    try:
        # Search for tweets
        tweets = await gather(twitter_api.search(query, limit=limit))
        
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
                id=str(tweet.id),
                url=tweet.url,
                date=tweet.date.isoformat(),
                content=tweet.rawContent,
                user={
                    "username": tweet.user.username,
                    "displayName": tweet.user.displayname,
                    "id": str(tweet.user.id),
                    "verified": tweet.user.verified,
                    "followersCount": tweet.user.followersCount,
                    "followingCount": tweet.user.followingCount,
                },
                metrics={
                    "retweets": tweet.retweetCount,
                    "likes": tweet.likeCount,
                    "replies": tweet.replyCount,
                    "quotes": tweet.quoteCount,
                    "bookmarks": tweet.bookmarkCount,
                    "views": tweet.viewCount or 0,
                },
                media=media_info
            ))
        
        return SearchResponse(
            query=query,
            tweets=processed_tweets,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching tweets: {str(e)}")

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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("railway_server:app", host="0.0.0.0", port=port, reload=False)
