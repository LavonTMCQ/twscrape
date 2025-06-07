import asyncio
from twscrape import API, gather

async def test_user_tweets():
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
    
    try:
        # First, get the user ID for @cashcoldgame
        print("Getting user profile for @cashcoldgame...")
        user = await api.user_by_login("cashcoldgame")
        
        if not user:
            print("User @cashcoldgame not found")
            return
            
        print(f"Found user: @{user.username} (ID: {user.id})")
        print(f"Display name: {user.displayname}")
        print(f"Followers: {user.followersCount}, Following: {user.friendsCount}")
        print(f"Total tweets: {user.statusesCount}")
        
        # Now get the user's tweets
        print(f"\nFetching tweets from @{user.username}...")
        tweets = await gather(api.user_tweets(user.id, limit=5))
        
        print(f"Found {len(tweets)} tweets:")
        for i, tweet in enumerate(tweets, 1):
            print(f"\n--- Tweet {i} ---")
            print(f"ID: {tweet.id}")
            print(f"Date: {tweet.date}")
            print(f"Content: {tweet.rawContent[:150]}...")
            print(f"Metrics: {tweet.replyCount} replies, {tweet.retweetCount} retweets, {tweet.likeCount} likes")
            
            # If the tweet has media, show that too
            if tweet.media and tweet.media.photos:
                print(f"Photos: {len(tweet.media.photos)}")
            if tweet.media and tweet.media.videos:
                print(f"Videos: {len(tweet.media.videos)}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_tweets())
