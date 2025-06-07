# Deploy Twitter Scraper API to Railway

This guide will help you deploy your Twitter scraper API to Railway so your agent can access it remotely.

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. Your Twitter cookies (from `cookie_string.txt` or `essential_cookies.json`)
3. Git repository (your current codebase)

## Step 1: Prepare Your Environment Variables

You'll need to set these environment variables in Railway:

### Required Variables:
- `TWITTER_COOKIE_STRING`: Your Twitter session cookies (content from `cookie_string.txt`)
- `TWITTER_USERNAME`: Your Twitter username (default: nuinui3478)
- `PORT`: 8000 (Railway will set this automatically)

### Optional Variables:
- `PYTHONPATH`: /app (already set in railway.toml)

## Step 2: Deploy to Railway

### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Connect to Railway:**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect the Dockerfile

3. **Set Environment Variables:**
   - In your Railway project dashboard
   - Go to "Variables" tab
   - Add the required environment variables listed above

### Option B: Deploy using Railway CLI

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize and deploy:**
   ```bash
   railway init
   railway up
   ```

4. **Set environment variables:**
   ```bash
   railway variables set TWITTER_COOKIE_STRING="your_cookie_string_here"
   railway variables set TWITTER_USERNAME="your_username"
   ```

## Step 3: Get Your Twitter Cookies

### From cookie_string.txt:
If you have `cookie_string.txt`, copy its entire content as the `TWITTER_COOKIE_STRING` environment variable.

### From essential_cookies.json:
If you have `essential_cookies.json`, convert it to cookie string format:
```bash
python -c "
import json
with open('essential_cookies.json', 'r') as f:
    cookies = json.load(f)
cookie_string = '; '.join([f'{k}={v}' for k, v in cookies.items()])
print(cookie_string)
"
```

## Step 4: Test Your Deployment

Once deployed, Railway will provide you with a URL like `https://your-app-name.railway.app`

Test the endpoints:

1. **Health check:**
   ```bash
   curl https://your-app-name.railway.app/
   ```

2. **Get user tweets:**
   ```bash
   curl "https://your-app-name.railway.app/api/user_tweets/cashcoldgame?limit=5"
   ```

3. **Search tweets:**
   ```bash
   curl "https://your-app-name.railway.app/api/search/bitcoin?limit=10"
   ```

4. **Check status:**
   ```bash
   curl https://your-app-name.railway.app/api/status
   ```

## Step 5: Configure Your Agent

Update your agent configuration to use the Railway URL instead of localhost:

```python
# Instead of: http://localhost:8000
# Use: https://your-app-name.railway.app

API_BASE_URL = "https://your-app-name.railway.app"
```

## Available Endpoints

Your hosted API will have these endpoints:

- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /api/user_tweets/{username}?limit=5` - Get user tweets
- `GET /api/search/{query}?limit=10` - Search tweets
- `GET /api/status` - API status and account info

## Monitoring and Logs

- View logs in Railway dashboard under "Deployments" tab
- Monitor resource usage in the "Metrics" tab
- Set up alerts for downtime or errors

## Troubleshooting

### Common Issues:

1. **"No active Twitter accounts found"**
   - Check your `TWITTER_COOKIE_STRING` environment variable
   - Ensure cookies are still valid (may need to refresh them)

2. **Port binding errors**
   - Railway automatically sets the PORT environment variable
   - Make sure your app uses `os.getenv("PORT", 8000)`

3. **Database issues**
   - The SQLite database is ephemeral on Railway
   - Accounts are re-added on each startup using cookies

4. **Rate limiting**
   - Twitter may rate limit your requests
   - Consider implementing request queuing or delays

## Security Notes

- Never commit your actual cookies to Git
- Use Railway's environment variables for sensitive data
- Regularly rotate your Twitter cookies
- Monitor for unusual API usage

## Cost Considerations

- Railway offers a free tier with limitations
- Monitor your usage to avoid unexpected charges
- Consider upgrading to a paid plan for production use
