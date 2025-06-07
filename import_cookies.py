import asyncio
import json
import os
from dotenv import load_dotenv
from twscrape import API

# Load environment variables
load_dotenv()

async def import_cookies():
    # Initialize API
    api = API()
    
    # Get credentials from environment variables
    username = os.getenv("TWITTER_USERNAME")
    password = os.getenv("TWITTER_PASSWORD")
    email = os.getenv("TWITTER_EMAIL")
    email_password = os.getenv("TWITTER_EMAIL_PASSWORD")
    
    if not all([username, password, email, email_password]):
        print("Error: Twitter credentials not properly configured. Check your .env file.")
        return
    
    # Prompt for cookies
    print("\nPlease paste your Twitter cookies in JSON format.")
    print("Example format: {\"auth_token\": \"value\", \"ct0\": \"value\", ...}")
    print("Enter your cookies (paste and press Enter twice when done):")
    
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    
    cookies_str = "".join(lines)
    
    try:
        cookies = json.loads(cookies_str)
        
        # Add account with cookies
        await api.pool.add_account(
            username=username,
            password=password,
            email=email,
            email_password=email_password,
            cookies=cookies
        )
        
        print(f"\nCookies successfully imported for account: {username}")
        
        # Save to database
        print("Account information saved to database.")
        
        # Test the connection
        print("\nTesting connection with imported cookies...")
        try:
            user = await api.user_by_login("elonmusk")
            if user:
                print(f"Success! Retrieved user: @{user.username} ({user.displayname})")
                print(f"Followers: {user.followersCount:,}")
                print("Your cookies are working correctly!")
            else:
                print("Error: Could not retrieve user information.")
        except Exception as e:
            print(f"Error testing connection: {e}")
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON format. Please check your cookies format and try again.")
    except Exception as e:
        print(f"Error importing cookies: {e}")

if __name__ == "__main__":
    asyncio.run(import_cookies())
