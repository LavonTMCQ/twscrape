import asyncio
from twscrape import API, gather

async def test_with_cookie_string():
    # Initialize API
    api = API()
    
    # Load cookie string
    with open("cookie_string.txt", "r") as f:
        cookie_string = f.read().strip()
    
    # Add account with cookie string
    username = "nuinui3478"  # Your Twitter username
    
    # Add the account
    await api.pool.add_account(
        username=username,
        password="",  # Not needed with cookies
        email="",     # Not needed with cookies
        email_password="",  # Not needed with cookies
        cookies=cookie_string
    )
    
    # Check account status
    accounts_info = await api.pool.accounts_info()
    for account in accounts_info:
        account_dict = dict(account)
        print(f"Username: {account_dict['username']}")
        print(f"Active: {account_dict['active']}")
        print(f"Error: {account_dict['error_msg']}")
    
    # Try a simple search
    ticker = "AAPL"
    print(f"\nSearching for ${ticker}...")
    
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
    asyncio.run(test_with_cookie_string())
