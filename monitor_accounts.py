import asyncio
import json
from datetime import datetime, timedelta
from twscrape import API, gather

async def monitor_user_tweets(username, limit=10, days_back=7):
    """
    Get recent tweets from a specific user.
    
    Args:
        username: Twitter username to monitor
        limit: Maximum number of tweets to retrieve
        days_back: Only include tweets from the last X days
    
    Returns:
        List of tweets
    """
    # Initialize API
    api = API()
    
    # Load cookie string
    with open("cookie_string.txt", "r") as f:
        cookie_string = f.read().strip()
    
    # Add account with cookie string
    await api.pool.add_account(
        username="nuinui3478",  # Your Twitter username
        password="",  # Not needed with cookies
        email="",     # Not needed with cookies
        email_password="",  # Not needed with cookies
        cookies=cookie_string
    )
    
    # First get the user ID from the username
    try:
        user = await api.user_by_login(username)
        if not user:
            print(f"User @{username} not found")
            return []
        
        print(f"\nMonitoring @{user.username} ({user.displayname})")
        print(f"Followers: {user.followersCount:,}, Tweets: {user.statusesCount:,}")
        
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get user tweets
        tweets = await gather(api.user_tweets(user.id, limit=limit))
        
        # Filter tweets by date if needed
        recent_tweets = [t for t in tweets if t.date > cutoff_date]
        
        print(f"Retrieved {len(recent_tweets)} tweets from the last {days_back} days")
        
        return recent_tweets
    
    except Exception as e:
        print(f"Error monitoring @{username}: {e}")
        return []

async def process_tweets(tweets):
    """Process and display tweets"""
    for i, tweet in enumerate(tweets, 1):
        print(f"\n--- Tweet {i} ---")
        print(f"Date: {tweet.date}")
        print(f"Content: {tweet.rawContent}")
        print(f"Likes: {tweet.likeCount}, Retweets: {tweet.retweetCount}, Replies: {tweet.replyCount}")
        
        # Check if this is a stock-related tweet (example filter)
        stock_symbols = find_stock_symbols(tweet.rawContent)
        if stock_symbols:
            print(f"Stock symbols mentioned: {', '.join(stock_symbols)}")

def find_stock_symbols(text):
    """Find stock symbols in text (starting with $)"""
    import re
    # Match $SYMBOL pattern (letters and numbers, at least 1 character)
    matches = re.findall(r'\$([A-Za-z][A-Za-z0-9]*)', text)
    return matches

async def main():
    # List of Twitter accounts to monitor
    accounts_to_monitor = [
        "elonmusk",       # Elon Musk
        "jimcramer",      # Jim Cramer
        "unusual_whales", # Unusual Whales
        "DeItaone",       # Walter Bloomberg
        "CNBCnow"         # CNBC Breaking News
    ]
    
    # Monitor each account
    for account in accounts_to_monitor:
        tweets = await monitor_user_tweets(account, limit=5, days_back=3)
        if tweets:
            await process_tweets(tweets)
            print("\n" + "-"*50)
    
    # Example of how to save the data for your agent
    print("\nExample of saving data for your agent:")
    account = "elonmusk"  # Example account
    tweets = await monitor_user_tweets(account, limit=3)
    
    # Convert to a format suitable for your agent
    agent_data = []
    for tweet in tweets:
        agent_data.append({
            "id": tweet.id_str,
            "username": tweet.user.username,
            "date": tweet.date.isoformat(),
            "content": tweet.rawContent,
            "metrics": {
                "likes": tweet.likeCount,
                "retweets": tweet.retweetCount,
                "replies": tweet.replyCount
            },
            "stock_symbols": find_stock_symbols(tweet.rawContent)
        })
    
    # Print example of data your agent would receive
    print(json.dumps(agent_data, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
