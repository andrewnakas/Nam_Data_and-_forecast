# NAM Weather Forecast Viewer

![Test Status](https://github.com/andrewnakas/Nam_Data_and-_forecast/actions/workflows/test.yml/badge.svg)

A Python backend + HTML frontend application for retrieving and displaying NAM (North American Mesoscale) forecast data from NOAA.

## Features

- Fetches 3-day hourly forecast data from NAM model
- Displays weather data at multiple pressure levels (1000mb, 925mb, 850mb, 700mb, 500mb, 300mb, 250mb)
- Shows temperature, wind (speed/direction/components), precipitation, and humidity data
- Interactive web interface with charts and tables
- Support for any location within NAM coverage area (North America)

## Requirements

- Python 3.8+
- Internet connection to access NOAA NOMADS servers

## Installation

1. Clone this repository or download the files

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask backend server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter a latitude and longitude (or use the preset locations) and click "Get Forecast"

## API Endpoints

### GET /api/forecast
Retrieve NAM forecast data for a specific location.

**Query Parameters:**
- `lat` (required): Latitude (-90 to 90)
- `lon` (required): Longitude (-180 to 180)
- `hours` (optional): Number of forecast hours (1-84, default: 72)

**Example:**
```
http://localhost:5000/api/forecast?lat=40.7128&lon=-74.0060&hours=72
```

### GET /api/status
Check if NAM data is currently available.

**Example Response:**
```json
{
  "status": "available",
  "latest_run": "2024-01-15T12:00:00",
  "dataset_url": "https://nomads.ncep.noaa.gov/dods/nam/nam20240115/nam_conusnest_12z"
}
```

## Data Variables

### Surface Data
- Temperature at 2m or surface (°C)
- Wind speed and direction at 10m (m/s, degrees)
- Wind U and V components at 10m (m/s)
- Precipitation accumulation or rate (mm)

### Pressure Level Data (at 1000, 925, 850, 700, 500, 300, 250 mb)
- Temperature (°C)
- Wind speed and direction (m/s, degrees)
- Wind U and V components (m/s)
- Relative humidity (%)
- Geopotential height (m)

## Data Source

This application retrieves data from NOAA's NOMADS (NCEP Operational Model Archive and Distribution System) servers:
- https://nomads.ncep.noaa.gov/

NAM model runs 4 times daily at 00, 06, 12, and 18 UTC.

## Testing

### Running Tests

Run the test suite:
```bash
python -m unittest test_app.py -v
```

Or run the health check:
```bash
python health_check.py http://localhost:5000
```

### GitHub Actions

This project includes automated testing via GitHub Actions. Tests run on:
- Every push to main/master/develop branches and claude/** branches
- Every pull request

The workflow tests:
- Unit tests across Python 3.9, 3.10, and 3.11
- Flask app startup
- API endpoint responses
- Project structure validation

## Deployment

This project includes **TWO deployment options**:

### Option 1: GitHub Pages (Static Version) - 100% FREE! ⭐

**Best for:** Most users who want a working app with no cost or server management

A fully static version that runs entirely on GitHub infrastructure:
- ✅ **FREE** hosting on GitHub Pages
- ✅ Automatic data updates every 6 hours via GitHub Actions
- ✅ No server management needed
- ✅ 15 preset U.S. cities
- ❌ Cannot query arbitrary coordinates
- ❌ 6-hour update delay

**Setup:** See detailed instructions in [GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md)

**Quick Start:**
1. Enable GitHub Pages in Settings → Pages → Deploy from `/docs` folder
2. Enable GitHub Actions with write permissions
3. Manually trigger "Fetch NAM Data and Deploy to GitHub Pages" workflow
4. Visit `https://{username}.github.io/{repo-name}/`

### Option 2: Full Backend Version (Flask Server)

**Best for:** Power users who need real-time data for any location

Deploy the full Python backend to get:
- ✅ Any lat/lon coordinates supported
- ✅ Real-time data fetching
- ✅ More flexible
- ❌ Requires paid hosting
- ❌ Server management needed

**Platforms:** Railway, Render, Heroku, AWS, Google Cloud, and more

**Setup:** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions

Quick options:
- **Railway** (recommended): Auto-deploys from GitHub with zero config
- **Render**: Free tier with easy setup
- **Fly.io**: Free tier, simple CLI deployment

## Troubleshooting

### "Could not find valid NAM dataset" error
- NAM data may be delayed or unavailable temporarily
- Try again in 15-30 minutes
- Check NOAA NOMADS status: https://nomads.ncep.noaa.gov/

### Connection errors
- Ensure you have internet connectivity
- NOAA servers may be experiencing high load
- Firewall may be blocking outbound connections

### Installation issues with netCDF4
If you encounter issues installing netCDF4:
- On Ubuntu/Debian: `sudo apt-get install libnetcdf-dev`
- On macOS: `brew install netcdf`
- On Windows: Consider using Anaconda/Miniconda

## Project Structure

```
.
├── app.py                      # Flask backend server
├── fetch_data.py               # Data fetcher for GitHub Pages
├── test_app.py                 # Unit tests
├── health_check.py             # Health check script
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version for Heroku
├── Procfile                    # Process file for deployment
├── run.sh                      # Startup script
├── README.md                   # This file
├── DEPLOYMENT.md               # Full backend deployment guide
├── GITHUB_PAGES_SETUP.md       # GitHub Pages setup guide
├── .github/
│   └── workflows/
│       ├── test.yml            # Unit testing workflow
│       └── deploy-pages.yml    # GitHub Pages deployment workflow
├── docs/                       # GitHub Pages static site
│   ├── index.html              # Static main page
│   ├── app.js                  # Static frontend JS
│   ├── style.css               # Static styles
│   ├── _config.yml             # Jekyll config
│   ├── README.md               # Pages documentation
│   └── data/
│       ├── index.json          # City index (auto-generated)
│       └── *.json              # City forecast files (auto-generated)
├── templates/                  # Flask backend templates
│   └── index.html              # Backend main page
└── static/                     # Flask backend static files
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## License

This project is provided as-is for educational and research purposes.

## Credits

- Weather data provided by NOAA/NCEP
- NAM model documentation: https://www.emc.ncep.noaa.gov/index.php?branch=NAM
