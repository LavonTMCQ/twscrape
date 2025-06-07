import asyncio
import json
import os
from twscrape import API, gather

async def run_direct_scrape():
    # Initialize API
    api = API()
    
    # Load cookies from file
    cookies_file = "twitter_cookies.json"
    username = "nuinui3478"  # Use your Twitter username
    
    if os.path.exists(cookies_file):
        try:
            with open(cookies_file, 'r') as f:
                cookies = json.load(f)
            print(f"Loaded cookies from {cookies_file}")
            
            # Add account with cookies
            await api.pool.add_account(
                username=username,
                password="",  # Not needed with cookies
                email="",     # Not needed with cookies
                email_password="",  # Not needed with cookies
                cookies=cookies
            )
            
            # Check if account is active
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
                
        except Exception as e:
            print(f"Error loading cookies: {e}")
    else:
        print(f"Cookies file {cookies_file} not found")

if __name__ == "__main__":
    asyncio.run(run_direct_scrape())
