import asyncio
from twscrape import API

async def test_user_profile():
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
    
    # Try getting a user profile
    try:
        # Get user profile for Elon Musk
        user = await api.user_by_login("elonmusk")
        
        if user:
            print(f"\nUser Profile:")
            print(f"Username: @{user.username}")
            print(f"Display Name: {user.displayname}")
            print(f"Followers: {user.followersCount:,}")
            print(f"Following: {user.friendsCount:,}")
            print(f"Tweets: {user.statusesCount:,}")
            print(f"Verified: {user.verified}")
            print(f"Blue: {user.blue}")
            print(f"Description: {user.rawDescription}")
        else:
            print("User not found")
    except Exception as e:
        print(f"Error getting user profile: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_profile())
