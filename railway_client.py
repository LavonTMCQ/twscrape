#!/usr/bin/env python3
"""
Client for interacting with the Railway-hosted Twitter Scraper API.
This is what your agent should use to access the hosted API.
"""

import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class TwitterAPIClient:
    """Client for the Railway-hosted Twitter Scraper API"""
    
    def __init__(self, base_url: str):
        """
        Initialize the client with the Railway app URL.
        
        Args:
            base_url: The Railway app URL (e.g., https://your-app-name.railway.app)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TwitterScraperAgent/1.0',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def detailed_health_check(self) -> Dict[str, Any]:
        """Get detailed health status including account information"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def get_user_tweets(self, username: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get tweets from a specific user.
        
        Args:
            username: Twitter username (without @)
            limit: Number of tweets to return (1-100)
        
        Returns:
            Dictionary containing user tweets data
        """
        try:
            params = {"limit": limit}
            response = self.session.get(
                f"{self.base_url}/api/user_tweets/{username}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "username": username}
    
    def search_tweets(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for tweets with a specific query.
        
        Args:
            query: Search query
            limit: Number of tweets to return (1-100)
        
        Returns:
            Dictionary containing search results
        """
        try:
            params = {"limit": limit}
            response = self.session.get(
                f"{self.base_url}/api/search/{query}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "query": query}
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API status and account information"""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "error"}
    
    def is_healthy(self) -> bool:
        """Check if the API is healthy and ready to use"""
        health = self.detailed_health_check()
        return health.get("status") == "healthy" and health.get("active_accounts", False)

# Example usage and testing functions
def test_api(base_url: str):
    """Test the API with various endpoints"""
    client = TwitterAPIClient(base_url)
    
    print(f"🧪 Testing API at: {base_url}")
    print("=" * 50)
    
    # Health check
    print("1. Health Check:")
    health = client.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    
    # Detailed health check
    print("\n2. Detailed Health Check:")
    detailed_health = client.detailed_health_check()
    print(f"   Status: {detailed_health.get('status', 'unknown')}")
    print(f"   Active Accounts: {detailed_health.get('active_accounts', False)}")
    
    if not client.is_healthy():
        print("❌ API is not healthy. Check your deployment and cookies.")
        return
    
    # Test user tweets
    print("\n3. Testing User Tweets (cashcoldgame):")
    user_tweets = client.get_user_tweets("cashcoldgame", limit=3)
    if "error" in user_tweets:
        print(f"   Error: {user_tweets['error']}")
    else:
        print(f"   Found {len(user_tweets.get('tweets', []))} tweets")
        if user_tweets.get('tweets'):
            latest_tweet = user_tweets['tweets'][0]
            print(f"   Latest: {latest_tweet['content'][:100]}...")
    
    # Test search
    print("\n4. Testing Search (bitcoin):")
    search_results = client.search_tweets("bitcoin", limit=3)
    if "error" in search_results:
        print(f"   Error: {search_results['error']}")
    else:
        print(f"   Found {len(search_results.get('tweets', []))} tweets")
        if search_results.get('tweets'):
            first_result = search_results['tweets'][0]
            print(f"   First result: {first_result['content'][:100]}...")
    
    # API status
    print("\n5. API Status:")
    status = client.get_api_status()
    if "error" in status:
        print(f"   Error: {status['error']}")
    else:
        print(f"   Status: {status.get('status', 'unknown')}")
        accounts = status.get('accounts', [])
        print(f"   Accounts: {len(accounts)} configured")
    
    print("\n✅ API testing complete!")

def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python railway_client.py <railway_app_url> [test]")
        print("Example: python railway_client.py https://your-app-name.railway.app test")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "test":
        test_api(base_url)
    else:
        # Simple health check
        client = TwitterAPIClient(base_url)
        health = client.health_check()
        print(json.dumps(health, indent=2))

if __name__ == "__main__":
    main()
