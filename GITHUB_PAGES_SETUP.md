# GitHub Pages Setup Guide

This guide explains how to deploy the NAM Weather Forecast app to GitHub Pages with automated data updates.

## Overview

The GitHub Pages version works by:
1. GitHub Actions runs every 6 hours to fetch NAM data
2. Data is saved as static JSON files
3. Static HTML/JS/CSS served from the `docs/` folder
4. No backend server needed - fully static!

## Step-by-Step Setup

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: Select your main branch (usually `main` or `master`)
   - **Folder**: Select `/docs`
5. Click **Save**

### 2. Enable GitHub Actions

1. Still in **Settings**
2. Click **Actions** > **General** (left sidebar)
3. Under "Actions permissions":
   - Select **Allow all actions and reusable workflows**
4. Under "Workflow permissions":
   - Select **Read and write permissions**
   - Check **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

### 3. Run the Data Fetch Workflow Manually (First Time)

1. Go to **Actions** tab in your repository
2. Click **Fetch NAM Data and Deploy to GitHub Pages** workflow
3. Click **Run workflow** button
4. Select your branch
5. Click **Run workflow**

The workflow will:
- Fetch NAM data for 15 preset cities
- Save JSON files to `docs/data/`
- Commit the changes
- Deploy to GitHub Pages

### 4. Wait for Deployment

- First deployment takes 2-5 minutes
- Check the Actions tab to monitor progress
- Once complete, your site will be at: `https://{username}.github.io/{repository-name}/`

### 5. Verify It Works

Visit your GitHub Pages URL. You should see:
- Dropdown list of 15 cities
- Last update timestamp
- Ability to select a city and view forecast data

## Automated Updates

After initial setup, GitHub Actions will:
- Run automatically every 6 hours (at 00:00, 06:00, 12:00, 18:00 UTC)
- Fetch fresh NAM forecast data
- Update the JSON files
- Redeploy to GitHub Pages

## Troubleshooting

### GitHub Pages shows 404

**Solution:**
- Make sure Pages is enabled in Settings > Pages
- Verify source is set to `/docs` folder from your main branch
- Wait 2-5 minutes after enabling Pages
- Check Actions tab for deployment status

### No data appears on the site

**Solution:**
1. Go to Actions tab
2. Manually run the "Fetch NAM Data and Deploy to GitHub Pages" workflow
3. Wait for it to complete
4. Refresh your GitHub Pages site

### Workflow fails with permission errors

**Solution:**
1. Go to Settings > Actions > General
2. Under "Workflow permissions" select "Read and write permissions"
3. Save and rerun the workflow

### NAM data is unavailable

**Reason:**
- NAM model data may be delayed (normal)
- NOAA servers may be temporarily unavailable
- Network connectivity issues

**Solution:**
- The workflow includes `continue-on-error: true` so it won't fail
- Wait for the next scheduled run (every 6 hours)
- Data usually becomes available 2-4 hours after model run time

### Want to change update frequency?

Edit `.github/workflows/deploy-pages.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  # Change to:
  - cron: '0 */3 * * *'  # Every 3 hours
  # or:
  - cron: '0 0,12 * * *' # Twice daily (midnight and noon UTC)
```

### Want to add more cities?

Edit `fetch_data.py` and add to the `LOCATIONS` list:

```python
LOCATIONS = [
    # ... existing cities ...
    {"name": "Your City, ST", "lat": 40.0, "lon": -105.0},
]
```

Commit and push. The next workflow run will include your new city.

## Manual Testing Locally

You can test the static site locally:

```bash
# Option 1: Python HTTP server
cd docs
python -m http.server 8000
# Visit http://localhost:8000

# Option 2: Any other static server
cd docs
npx serve
```

## Files Overview

```
docs/
├── index.html          # Main page
├── app.js             # Frontend logic
├── style.css          # Styling
├── _config.yml        # Jekyll config (optional)
├── README.md          # Docs README
└── data/
    ├── index.json     # City index
    └── *.json         # Individual city data
```

## Customization

### Change color scheme

Edit `docs/style.css`:
- Line 9: `background: linear-gradient(...)`  - Main gradient
- Line 238: `background: #667eea;` - Table headers
- Line 329: `color: #667eea;` - Links

### Change cities displayed

Edit `fetch_data.py` - modify the `LOCATIONS` array

### Change forecast length

Edit `fetch_data.py` - line ~43:
```python
hours=72  # Change to 24, 48, or up to 84
```

## Cost

**100% FREE!**
- GitHub Pages: Free for public repositories
- GitHub Actions: 2000 minutes/month free
- This workflow uses ~5 minutes per run = 4 runs/day = 600 minutes/month
- Well within free tier!

## Performance

- Static site loads instantly
- No backend = no server costs
- Data updates every 6 hours (not real-time, but sufficient for forecasts)
- CDN-backed via GitHub Pages
- Mobile-friendly responsive design

## Limitations vs Full Backend

**GitHub Pages Version:**
- ✅ Free hosting
- ✅ No server management
- ✅ Automatic updates
- ❌ Only preset cities
- ❌ 6-hour update delay
- ❌ Can't query arbitrary coordinates

**Full Backend Version:**
- ✅ Any lat/lon coordinates
- ✅ Real-time data fetching
- ✅ More flexible
- ❌ Requires paid hosting
- ❌ Server management needed

## Next Steps

After setup is complete:
1. Share your GitHub Pages URL with users
2. Monitor Actions tab to ensure scheduled runs succeed
3. Check data freshness (should update every 6 hours)
4. Customize cities/styling as needed

## Support

If you encounter issues:
1. Check the Actions tab for workflow failures
2. Review workflow logs for error messages
3. Verify GitHub Pages settings
4. Ensure workflow permissions are correct
5. Try manually triggering the workflow
