import requests
import json
from typing import Dict, Any, List, Optional

class TwitterScraperClient:
    """
    A client for interacting with the Twitter Scraper API.
    This can be used by your agent to fetch Twitter data for stock tickers.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client with the API base URL.
        
        Args:
            base_url: The base URL of the Twitter Scraper API
        """
        self.base_url = base_url.rstrip('/')
    
    def get_ticker_tweets(
        self, 
        ticker: str, 
        limit: int = 5, 
        product: str = "Top"
    ) -> Dict[str, Any]:
        """
        Get tweets for a specific stock ticker.
        
        Args:
            ticker: The stock ticker symbol (e.g., AAPL, TSLA)
            limit: Number of tweets to return (default: 5)
            product: Search tab to use (default: Top)
            
        Returns:
            A dictionary containing the ticker data and tweets
        """
        url = f"{self.base_url}/api/search/{ticker}"
        params = {
            "limit": limit,
            "product": product
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get tweets: {str(e)}"}
    
    def get_accounts_info(self) -> Dict[str, Any]:
        """
        Get information about the configured Twitter accounts.
        
        Returns:
            A dictionary containing account information
        """
        url = f"{self.base_url}/api/accounts"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get account info: {str(e)}"}
    
    def extract_sentiment(self, ticker_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract sentiment information from ticker data.
        
        Args:
            ticker_data: The data returned from get_ticker_tweets()
            
        Returns:
            A dictionary containing sentiment information
        """
        if "error" in ticker_data:
            return {"error": ticker_data["error"]}
        
        try:
            return {
                "ticker": ticker_data["ticker"],
                "overall_sentiment": ticker_data.get("overall_sentiment", {}),
                "tweet_count": len(ticker_data["tweets"]),
                "timestamp": ticker_data["timestamp"]
            }
        except KeyError as e:
            return {"error": f"Failed to extract sentiment: {str(e)}"}
    
    def summarize_tweets(self, ticker_data: Dict[str, Any], max_tweets: int = 3) -> str:
        """
        Create a human-readable summary of the tweets.
        
        Args:
            ticker_data: The data returned from get_ticker_tweets()
            max_tweets: Maximum number of tweets to include in the summary
            
        Returns:
            A string containing a summary of the tweets
        """
        if "error" in ticker_data:
            return f"Error: {ticker_data['error']}"
        
        try:
            ticker = ticker_data["ticker"]
            tweets = ticker_data["tweets"][:max_tweets]
            
            # Get overall sentiment if available
            sentiment_info = ""
            if "overall_sentiment" in ticker_data:
                sentiment = ticker_data["overall_sentiment"]
                sentiment_info = (
                    f"Overall sentiment: {sentiment.get('label', 'unknown')} "
                    f"(score: {sentiment.get('score', 'N/A')})"
                )
            
            # Build summary
            summary = [f"Summary for ${ticker} - {sentiment_info}"]
            
            for i, tweet in enumerate(tweets, 1):
                user = tweet["user"]["username"]
                followers = tweet["user"]["followers_count"]
                content = tweet["content"]
                sentiment = tweet.get("sentiment", {}).get("label", "unknown")
                
                summary.append(f"\n{i}. @{user} ({followers} followers) - Sentiment: {sentiment}")
                summary.append(f"   {content[:150]}...")
            
            return "\n".join(summary)
        
        except KeyError as e:
            return f"Failed to summarize tweets: {str(e)}"


# Example usage
if __name__ == "__main__":
    import sys
    
    # Get ticker from command line or use default
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    # Create client
    client = TwitterScraperClient()
    
    # Get tweets
    print(f"Fetching tweets for ${ticker}...")
    ticker_data = client.get_ticker_tweets(ticker, limit=5)
    
    # Print summary
    print("\n" + client.summarize_tweets(ticker_data))
    
    # Print full JSON (commented out to avoid cluttering the console)
    # print("\nFull response:")
    # print(json.dumps(ticker_data, indent=2))
