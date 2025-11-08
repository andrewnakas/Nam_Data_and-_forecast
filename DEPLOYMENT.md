# Deployment Guide

This NAM Weather Forecast application requires a Python backend server and **cannot** be deployed to GitHub Pages (which only hosts static sites). Below are several deployment options:

## Quick Deployment Options

### 1. Railway (Recommended - Free tier available)

Railway automatically detects Python apps and deploys them easily.

1. Sign up at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select this repository
4. Railway will auto-detect the Flask app and deploy it
5. Your app will be available at a generated URL

**No configuration needed** - Railway detects Flask automatically!

### 2. Render (Free tier available)

1. Sign up at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: nam-weather-forecast
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add environment variable: `PORT=5000`
6. Click "Create Web Service"

**Note**: Add `gunicorn` to requirements.txt:
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

### 3. Heroku (Free tier ended, paid plans available)

1. Install Heroku CLI: `curl https://cli-assets.heroku.com/install.sh | sh`
2. Login: `heroku login`
3. Create app: `heroku create nam-weather-forecast`
4. Deploy:
```bash
git push heroku main
```

**Required files** (add these):

**Procfile**:
```
web: gunicorn app:app
```

**runtime.txt**:
```
python-3.11.0
```

### 4. AWS Elastic Beanstalk

1. Install EB CLI: `pip install awsebcli`
2. Initialize: `eb init -p python-3.11 nam-weather-app`
3. Create environment: `eb create nam-weather-env`
4. Deploy: `eb deploy`

### 5. Google Cloud Run

1. Install gcloud CLI
2. Create Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD exec gunicorn --bind :$PORT app:app
```

3. Build and deploy:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/nam-weather
gcloud run deploy --image gcr.io/PROJECT-ID/nam-weather --platform managed
```

### 6. DigitalOcean App Platform

1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
2. Click "Create" → "Apps"
3. Connect GitHub repository
4. DigitalOcean auto-detects Flask and configures deployment
5. Click "Next" and deploy

### 7. Fly.io (Free tier available)

1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Launch: `fly launch`
4. Deploy: `fly deploy`

## Local Development

For local testing and development:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Access at http://localhost:5000
```

## Production Considerations

### Security
- Change `app.run(debug=True)` to `app.run(debug=False)` in production
- Use environment variables for sensitive configuration
- Add rate limiting to prevent API abuse
- Use HTTPS (most platforms provide this automatically)

### Performance
- Use a production WSGI server like Gunicorn or uWSGI
- Enable caching for frequently requested locations
- Consider adding Redis for session management
- Set up monitoring (New Relic, Datadog, etc.)

### Scalability
- Use a CDN for static files
- Implement request caching
- Add database for storing historical data
- Use background tasks for data fetching

## Environment Variables

For production deployments, consider adding these environment variables:

```bash
FLASK_ENV=production
PORT=5000
SECRET_KEY=your-secret-key-here
```

## Monitoring NOAA Data Availability

The app depends on NOAA NOMADS servers for NAM data. If data is unavailable:
- NAM runs 4 times daily (00, 06, 12, 18 UTC)
- Data may be delayed 2-4 hours after model run time
- Check NOAA status: https://nomads.ncep.noaa.gov/

## GitHub Pages Alternative (Static Version)

If you only want to display pre-fetched data without live updates, you could create a static version:

1. Pre-fetch data using the Python script
2. Save as JSON files
3. Use GitHub Pages to host HTML/CSS/JS that reads the JSON
4. Update JSON files on a schedule using GitHub Actions

However, this won't provide real-time data or user-specified locations.

## Testing the Deployment

After deploying, test these endpoints:

```bash
# Health check
curl https://your-app-url.com/api/status

# Get forecast
curl "https://your-app-url.com/api/forecast?lat=40.7128&lon=-74.0060&hours=24"

# Web interface
# Open browser to https://your-app-url.com
```

## Troubleshooting

**"Could not find valid NAM dataset"**
- NAM data may be delayed or processing
- Try again in 15-30 minutes
- Check NOAA NOMADS status

**Port binding errors**
- Ensure your platform's PORT environment variable is used
- Most platforms inject PORT automatically

**Module import errors**
- Verify all dependencies are in requirements.txt
- Check Python version compatibility (3.8+)

**Slow response times**
- First request may be slow as it fetches data from NOAA
- Consider implementing caching
- Use a faster hosting region closer to NOAA servers (US East)
