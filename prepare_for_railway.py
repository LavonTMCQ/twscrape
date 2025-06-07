#!/usr/bin/env python3
"""
Script to prepare your Twitter scraper for Railway deployment.
This script helps you format cookies and provides deployment instructions.
"""

import json
import os
import sys

def read_cookie_string():
    """Read cookie string from file"""
    cookie_file = "cookie_string.txt"
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r') as f:
            return f.read().strip()
    return None

def read_essential_cookies():
    """Read essential cookies from JSON file"""
    cookies_file = "essential_cookies.json"
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
            # Convert to cookie string format
            cookie_string = '; '.join([f'{k}={v}' for k, v in cookies.items()])
            return cookie_string
    return None

def main():
    print("🚀 Preparing Twitter Scraper for Railway Deployment")
    print("=" * 50)
    
    # Check for cookie files
    cookie_string = read_cookie_string()
    essential_cookies = read_essential_cookies()
    
    if not cookie_string and not essential_cookies:
        print("❌ Error: No cookie files found!")
        print("Please ensure you have either:")
        print("  - cookie_string.txt")
        print("  - essential_cookies.json")
        print("\nRun update_cookies.py or extract cookies manually first.")
        sys.exit(1)
    
    # Use cookie_string.txt if available, otherwise use essential_cookies.json
    final_cookie_string = cookie_string or essential_cookies
    
    print("✅ Cookie files found!")
    print(f"Cookie string length: {len(final_cookie_string)} characters")
    
    # Show deployment instructions
    print("\n📋 Railway Deployment Instructions:")
    print("=" * 50)
    
    print("\n1. Set this environment variable in Railway:")
    print("   Variable Name: TWITTER_COOKIE_STRING")
    print("   Variable Value:")
    print(f"   {final_cookie_string}")
    
    print("\n2. Optional environment variables:")
    print("   TWITTER_USERNAME=nuinui3478  (or your Twitter username)")
    
    print("\n3. Deploy using one of these methods:")
    print("   a) Push to GitHub and connect to Railway")
    print("   b) Use Railway CLI: railway up")
    
    print("\n4. Your API will be available at:")
    print("   https://your-app-name.railway.app")
    
    print("\n5. Test endpoints:")
    print("   GET /                                    - Health check")
    print("   GET /api/user_tweets/{username}?limit=5  - Get user tweets")
    print("   GET /api/search/{query}?limit=10         - Search tweets")
    print("   GET /api/status                          - API status")
    
    # Save cookie string to a temporary file for easy copying
    with open("railway_cookie_string.txt", "w") as f:
        f.write(final_cookie_string)
    
    print(f"\n💾 Cookie string saved to: railway_cookie_string.txt")
    print("   You can copy this file's content to Railway environment variables.")
    
    print("\n🔗 Useful links:")
    print("   Railway Dashboard: https://railway.app/dashboard")
    print("   Railway CLI: npm install -g @railway/cli")
    print("   Documentation: See deploy_to_railway.md")
    
    print("\n✨ Ready for deployment!")

if __name__ == "__main__":
    main()
