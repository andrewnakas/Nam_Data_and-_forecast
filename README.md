# NAM Weather Forecast Viewer

![Deploy Status](https://github.com/andrewnakas/Nam_Data_and-_forecast/actions/workflows/deploy-pages.yml/badge.svg)

A 100% free static GitHub Pages application that displays NAM (North American Mesoscale) forecast data from NOAA with automated updates every 6 hours.

## Features

- ✅ **FREE** hosting on GitHub Pages
- ✅ Automatic updates every 6 hours via GitHub Actions
- ✅ No server management needed
- ✅ 72-hour forecasts for 15 major U.S. cities
- ✅ Surface data + 7 pressure levels (1000, 925, 850, 700, 500, 300, 250 mb)
- ✅ Temperature in °C and °F
- ✅ Wind speed in m/s and mph
- ✅ Precipitation data
- ✅ Interactive charts with Chart.js
- ✅ Mobile-responsive design

## Cities Included

New York, Los Angeles, Chicago, Houston, Phoenix, Philadelphia, San Antonio, San Diego, Dallas, Denver, Seattle, Miami, Atlanta, Boston, Detroit

## Live Demo

Once deployed, your site will be at:
```
https://{your-username}.github.io/Nam_Data_and-_forecast/
```

## Quick Setup (3 Steps)

### 1. Enable GitHub Pages

1. Go to your repository **Settings** → **Pages**
2. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: Select `main`, `master`, or your branch
   - **Folder**: Select `/docs`
3. Click **Save**

### 2. Enable GitHub Actions

1. Go to **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - Select **"Read and write permissions"**
   - Check **"Allow GitHub Actions to create and approve pull requests"**
3. Click **Save**

### 3. Run First Deployment

1. Go to **Actions** tab
2. Click **"Deploy to GitHub Pages"** workflow
3. Click **"Run workflow"** button
4. Select your branch and click **"Run workflow"**
5. Wait 3-5 minutes for deployment to complete

That's it! Your site is now live and will auto-update every 6 hours.

## How It Works

Every 6 hours (synchronized with NAM model runs at 00, 06, 12, 18 UTC):

1. GitHub Actions runs `fetch_data.py`
2. Fetches latest NAM forecast for all 15 cities
3. Saves data as static JSON files in `docs/data/`
4. Commits files to repository
5. Automatically deploys to GitHub Pages

Users visit the site, select a city, and view the latest forecast - all with zero hosting costs!

## Data Provided

### Surface Data
- Temperature (2m)
- Wind speed and direction (10m)
- Precipitation

### Pressure Levels (1000, 925, 850, 700, 500, 300, 250 mb)
- Temperature
- Wind speed and direction
- Relative humidity
- Geopotential height

All data shown in both metric and imperial units.

## Project Structure

```
.
├── docs/                       # GitHub Pages site (this gets deployed!)
│   ├── index.html              # Main page
│   ├── app.js                  # Frontend JavaScript
│   ├── style.css               # Styling
│   └── data/                   # Auto-generated forecast data
│       ├── index.json          # City index
│       └── *.json              # Individual city forecasts
│
├── .github/workflows/
│   └── deploy-pages.yml        # Automated deployment workflow
│
├── fetch_data.py               # Script to fetch NAM data
├── GITHUB_PAGES_SETUP.md       # Detailed setup guide
└── README.md                   # This file
```

## Customization

### Change Update Frequency

Edit `.github/workflows/deploy-pages.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  # Change to:
  - cron: '0 */3 * * *'  # Every 3 hours
```

### Add More Cities

Edit `fetch_data.py`:
```python
LOCATIONS = [
    # ... existing cities ...
    {"name": "Your City, ST", "lat": 40.0, "lon": -105.0},
]
```

## Troubleshooting

### Site shows 404
- Wait 2-5 minutes after enabling Pages
- Check Settings → Pages shows deployment URL
- Verify `/docs` folder is selected

### No data appears
- Manually run "Deploy to GitHub Pages" workflow from Actions tab
- Wait for workflow to complete
- Refresh your site

### Data fetch fails
- NAM data may be delayed (normal)
- Workflow will retry in 6 hours automatically
- Check Actions tab for detailed logs

## Cost

**$0** - Completely free!
- GitHub Pages: Free for public repos
- GitHub Actions: 2,000 free minutes/month
- This workflow uses ~10 min per run × 4 runs/day = 1,200 min/month
- Well within free tier!

## Data Source

Weather data from NOAA NAM (North American Mesoscale) Model
https://nomads.ncep.noaa.gov/

NAM runs 4 times daily at 00, 06, 12, and 18 UTC

## Advanced: Flask Backend Option

For power users who need real-time data for any coordinates, a Flask backend version is also included. See `app.py` and `DEPLOYMENT.md` for hosting on Railway, Render, etc.

## License

This project is provided as-is for educational and research purposes.

## Credits

- Weather data provided by NOAA/NCEP
- NAM model documentation: https://www.emc.ncep.noaa.gov/index.php?branch=NAM
