import asyncio
import json
from twscrape import API, gather

async def test_with_essential_cookies():
    # Initialize API
    api = API()
    
    # Load essential cookies
    with open("essential_cookies.json", "r") as f:
        cookies = json.load(f)
    
    # Add account with just the essential cookies
    username = "nuinui3478"  # Your Twitter username
    
    # Add the account
    await api.pool.add_account(
        username=username,
        password="",  # Not needed with cookies
        email="",     # Not needed with cookies
        email_password="",  # Not needed with cookies
        cookies=cookies
    )
    
    # Force the account to be active
    for account in api.pool.accounts:
        if account.username == username:
            account.active = True
            break
    
    # Try a simple search
    ticker = "AAPL"
    print(f"Searching for ${ticker}...")
    
    try:
        # Get tweets
        tweets = await gather(api.search(f"${ticker}", limit=5))
        
        print(f"Found {len(tweets)} tweets:")
        for i, tweet in enumerate(tweets, 1):
            print(f"\n--- Tweet {i} ---")
            print(f"User: @{tweet.user.username}")
            print(f"Date: {tweet.date}")
            print(f"Content: {tweet.rawContent[:100]}...")
            print(f"Likes: {tweet.likeCount}, Retweets: {tweet.retweetCount}")
    except Exception as e:
        print(f"Error searching: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_essential_cookies())
