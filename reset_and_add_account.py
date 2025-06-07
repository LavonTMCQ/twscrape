import asyncio
import json
import os
import sqlite3
from twscrape import API, AccountsPool

async def reset_and_add_account():
    # Delete the existing database to start fresh
    db_file = "accounts.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Deleted existing database: {db_file}")
    
    # Initialize a new API and accounts pool
    pool = AccountsPool(db_file)
    api = API(pool)
    
    # Load cookies from file
    cookies_file = "twitter_cookies.json"
    username = "nuinui3478"  # Use your Twitter username
    
    if os.path.exists(cookies_file):
        try:
            with open(cookies_file, 'r') as f:
                cookies = json.load(f)
            print(f"Loaded cookies from {cookies_file}")
            
            # Add account with cookies and set it as active
            await pool.add_account(
                username=username,
                password="",  # Not needed with cookies
                email="",     # Not needed with cookies
                email_password="",  # Not needed with cookies
                cookies=cookies
            )
            
            # Manually set the account as active in the database
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET active = 1 WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            print(f"Manually set account {username} as active in the database")
            
            # Check if account is active
            accounts_info = await pool.accounts_info()
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
                tweets = await api.search(f"${ticker}", limit=5)
                count = 0
                
                async for tweet in tweets:
                    count += 1
                    print(f"\n--- Tweet {count} ---")
                    print(f"User: @{tweet.user.username}")
                    print(f"Date: {tweet.date}")
                    print(f"Content: {tweet.rawContent[:100]}...")
                    print(f"Likes: {tweet.likeCount}, Retweets: {tweet.retweetCount}")
                    
                    if count >= 5:
                        break
                        
                if count == 0:
                    print("No tweets found.")
            except Exception as e:
                print(f"Error searching: {e}")
                
        except Exception as e:
            print(f"Error loading cookies: {e}")
    else:
        print(f"Cookies file {cookies_file} not found")

if __name__ == "__main__":
    asyncio.run(reset_and_add_account())
