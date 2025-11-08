# NAM Weather Forecast - GitHub Pages Version

This is the static GitHub Pages version of the NAM Weather Forecast application.

## How It Works

1. **GitHub Actions** runs every 6 hours (synchronized with NAM model runs at 00, 06, 12, 18 UTC)
2. Python script fetches forecast data for 15 preset U.S. cities
3. Data is saved as static JSON files in the `data/` directory
4. Files are committed back to the repository
5. GitHub Pages serves the static HTML/CSS/JavaScript
6. Users select a city from the dropdown to view forecast data

## Features

- 72-hour (3-day) forecast for 15 major U.S. cities
- Surface weather: Temperature (°C and °F), wind speed (m/s and mph), precipitation
- Multiple pressure levels: 1000, 925, 850, 700, 500, 300, 250 mb
- Interactive charts using Chart.js
- Automatic updates every 6 hours
- 100% static - no backend server needed

## Preset Locations

- New York, NY
- Los Angeles, CA
- Chicago, IL
- Houston, TX
- Phoenix, AZ
- Philadelphia, PA
- San Antonio, TX
- San Diego, CA
- Dallas, TX
- Denver, CO
- Seattle, WA
- Miami, FL
- Atlanta, GA
- Boston, MA
- Detroit, MI

## Data Source

Weather data from NOAA NAM (North American Mesoscale) Model via NOMADS OpenDAP servers.

## Limitations

- Only preset cities available (cannot query arbitrary coordinates)
- Data updates every 6 hours (not real-time)
- Requires GitHub Actions to run successfully
- Subject to NOAA data availability

## Files

- `index.html` - Main page
- `app.js` - Frontend JavaScript
- `style.css` - Styling
- `data/` - JSON data files
  - `index.json` - Location index
  - `{city}.json` - Individual city forecasts
