#!/usr/bin/env python3
"""
Twitter Cookie Updater

This script helps you update your Twitter cookies when they expire.
It will prompt you to enter the new cookies and save them to cookie_string.txt.
"""

import os
import sys
import json
import requests

def update_cookies():
    print("Twitter Cookie Updater")
    print("======================")
    print("\nThis script will help you update your Twitter cookies.")
    print("You'll need to extract the following cookies from your browser:")
    print("  - auth_token")
    print("  - ct0")
    print("  - twid")
    print("\nInstructions:")
    print("1. Log in to Twitter in your browser")
    print("2. Open developer tools (F12 or right-click > Inspect)")
    print("3. Go to the Application/Storage tab")
    print("4. Click on Cookies > twitter.com or x.com")
    print("5. Find and copy the values for the cookies listed above")
    
    # Get cookie values
    auth_token = input("\nEnter auth_token value: ").strip()
    ct0 = input("Enter ct0 value: ").strip()
    twid = input("Enter twid value: ").strip()
    
    if not all([auth_token, ct0, twid]):
        print("\nError: All cookie values are required.")
        return False
    
    # Format cookie string
    cookie_string = f"auth_token={auth_token}; ct0={ct0}; twid={twid}"
    
    # Save to file
    try:
        with open("cookie_string.txt", "w") as f:
            f.write(cookie_string)
        print("\nCookies successfully saved to cookie_string.txt")
        
        # Test the cookies
        print("\nTesting cookies...")
        test_cookies(cookie_string)
        
        return True
    except Exception as e:
        print(f"\nError saving cookies: {e}")
        return False

def test_cookies(cookie_string):
    """Test if the cookies work by making a request to Twitter"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Cookie": cookie_string
    }
    
    try:
        response = requests.get("https://twitter.com/i/api/graphql/32pL5BWe9WKeSK1MoPvFQQ/UserByScreenName", 
                               params={"variables": json.dumps({"screen_name": "elonmusk"})},
                               headers=headers)
        
        if response.status_code == 200:
            print("Success! Cookies are working correctly.")
        else:
            print(f"Warning: Received status code {response.status_code} when testing cookies.")
            print("The cookies might not work correctly.")
    except Exception as e:
        print(f"Error testing cookies: {e}")

if __name__ == "__main__":
    update_cookies()
