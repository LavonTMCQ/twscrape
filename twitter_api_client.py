import requests
import json
import sys

def get_user_tweets(username, limit=5):
    """
    Get tweets from a specific Twitter user using our API.
    
    Args:
        username: Twitter username (without the @ symbol)
        limit: Number of tweets to return (default: 5)
        
    Returns:
        A dictionary containing the user's tweets and information
    """
    url = f"http://localhost:8000/api/user_tweets/{username}"
    params = {"limit": limit}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching tweets: {str(e)}"}

def print_tweets(data):
    """
    Print tweets in a readable format.
    
    Args:
        data: The response from get_user_tweets()
    """
    if "error" in data:
        print(f"Error: {data['error']}")
        return
    
    print(f"Tweets from @{data['username']} (User ID: {data['user_id']})")
    print(f"Retrieved at: {data['timestamp']}")
    print(f"Found {len(data['tweets'])} tweets:\n")
    
    for i, tweet in enumerate(data['tweets'], 1):
        print(f"--- Tweet {i} ---")
        print(f"Date: {tweet['date']}")
        print(f"Content: {tweet['content']}")
        print(f"Metrics: {tweet['metrics']['replies']} replies, {tweet['metrics']['retweets']} retweets, {tweet['metrics']['likes']} likes")
        
        if tweet.get('media'):
            if tweet['media'].get('photos'):
                print(f"Photos: {len(tweet['media']['photos'])}")
            if tweet['media'].get('videos'):
                print(f"Videos: {len(tweet['media']['videos'])}")
        
        print(f"URL: {tweet['url']}")
        print()

def main():
    # Get username from command line or use default
    username = sys.argv[1] if len(sys.argv) > 1 else "cashcoldgame"
    
    # Get limit from command line or use default
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Get tweets
    data = get_user_tweets(username, limit)
    
    # Print tweets
    print_tweets(data)
    
    # Optionally save to file
    if len(sys.argv) > 3 and sys.argv[3] == "--save":
        filename = f"{username}_tweets.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Tweets saved to {filename}")

if __name__ == "__main__":
    main()
