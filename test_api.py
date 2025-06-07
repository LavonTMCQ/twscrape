import asyncio
import json
import sys
from twscrape import API, gather
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def test_twitter_api():
    # Initialize API
    api = API()

    # Get credentials from environment variables
    username = os.getenv("TWITTER_USERNAME")
    password = os.getenv("TWITTER_PASSWORD")
    email = os.getenv("TWITTER_EMAIL")
    email_password = os.getenv("TWITTER_EMAIL_PASSWORD")
    proxy = os.getenv("TWITTER_PROXY")
    cookies_file = os.getenv("TWITTER_COOKIES_FILE", "twitter_cookies.json")

    # Load cookies if available
    cookies = None
    if os.path.exists(cookies_file):
        try:
            with open(cookies_file, 'r') as f:
                cookies = json.load(f)
            print(f"Loaded cookies from {cookies_file}")
        except Exception as e:
            print(f"Error loading cookies file: {e}")

    if not username:
        print("Error: Twitter username not configured. Check your .env file.")
        return

    # Add account to the pool with cookies
    await api.pool.add_account(
        username=username,
        password=password or "",
        email=email or "",
        email_password=email_password or "",
        proxy=proxy,
        cookies=cookies
    )

    # Check if account is active with cookies
    accounts_info = await api.pool.accounts_info()
    has_active = any(dict(account).get('active', False) for account in accounts_info)

    if not has_active and not cookies:
        # Try to login if we don't have cookies
        try:
            print("No active accounts with cookies. Trying to login...")
            await api.pool.login_all()
            print("Login successful!")
        except Exception as e:
            print(f"Error logging in: {e}")
            print("Consider using browser cookies for authentication.")
    elif has_active:
        print("Account is active with cookies!")
    else:
        print("Account is not active even with cookies. There might be an issue with the cookies.")

    # Get account info
    accounts_info = await api.pool.accounts_info()
    print("\nAccount Information:")
    for account in accounts_info:
        account_dict = dict(account)
        print(f"Username: {account_dict['username']}")
        print(f"Logged in: {account_dict['active']}")
        print(f"Last used: {account_dict['last_used']}")
        print(f"Error message: {account_dict['error_msg']}")
        print()

    # Test search functionality
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    else:
        ticker = "AAPL"  # Default ticker

    query = f"${ticker.upper()}"
    print(f"Searching for: {query}")

    try:
        # Search for tweets
        tweets = await gather(api.search(query, limit=5, kv={"product": "Top"}))

        print(f"\nFound {len(tweets)} tweets for {query}:")
        for i, tweet in enumerate(tweets, 1):
            print(f"\n--- Tweet {i} ---")
            print(f"ID: {tweet.id}")
            print(f"URL: {tweet.url}")
            print(f"Date: {tweet.date}")
            print(f"User: @{tweet.user.username} ({tweet.user.displayname})")
            print(f"Content: {tweet.rawContent[:100]}...")
            print(f"Metrics: {tweet.replyCount} replies, {tweet.retweetCount} retweets, {tweet.likeCount} likes")

    except Exception as e:
        print(f"Error searching Twitter: {e}")

if __name__ == "__main__":
    asyncio.run(test_twitter_api())
