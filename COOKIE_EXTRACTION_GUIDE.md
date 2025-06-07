# Twitter Cookie Extraction Guide

This guide will help you extract cookies from your browser after logging into Twitter, which can be used to bypass login issues with the Twitter scraper.

## Chrome Instructions

1. **Log in to Twitter**:
   - Open Chrome
   - Go to https://twitter.com (or https://x.com)
   - Log in with your credentials

2. **Open Developer Tools**:
   - Right-click anywhere on the page and select "Inspect"
   - Or press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac)

3. **Navigate to Application Tab**:
   - Click on the "Application" tab in the developer tools
   - In the left sidebar, expand "Cookies"
   - Click on "https://twitter.com" or "https://x.com"

4. **Extract Important Cookies**:
   - Look for the following cookies (at minimum):
     - `auth_token`
     - `ct0`
     - `twid`
   - For each cookie, note down the name and value

5. **Format Cookies as JSON**:
   - Create a JSON object with the cookie names and values, like this:
   ```json
   {
     "auth_token": "your_auth_token_value",
     "ct0": "your_ct0_value",
     "twid": "your_twid_value"
   }
   ```

## Firefox Instructions

1. **Log in to Twitter**:
   - Open Firefox
   - Go to https://twitter.com (or https://x.com)
   - Log in with your credentials

2. **Open Developer Tools**:
   - Right-click anywhere on the page and select "Inspect Element"
   - Or press `F12`

3. **Navigate to Storage Tab**:
   - Click on the "Storage" tab in the developer tools
   - In the left sidebar, expand "Cookies"
   - Click on "https://twitter.com" or "https://x.com"

4. **Extract Important Cookies**:
   - Look for the same cookies as mentioned in the Chrome instructions
   - Note down the name and value of each cookie

5. **Format Cookies as JSON** (same as Chrome instructions)

## Using the Cookies

1. Run the `import_cookies.py` script:
   ```bash
   python import_cookies.py
   ```

2. When prompted, paste the JSON object containing your cookies and press Enter twice.

3. The script will import your cookies and test the connection to Twitter.

4. If successful, you can now run the Twitter scraper API with these cookies.

## Important Notes

- Cookies expire after some time, so you may need to repeat this process periodically
- Do not share your cookies with anyone, as they provide access to your Twitter account
- Using cookies is more reliable than username/password authentication for Twitter scraping
