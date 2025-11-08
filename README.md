# NAM Weather Forecast Viewer

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
├── app.py                 # Flask backend server
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       └── app.js        # Frontend JavaScript
```

## License

This project is provided as-is for educational and research purposes.

## Credits

- Weather data provided by NOAA/NCEP
- NAM model documentation: https://www.emc.ncep.noaa.gov/index.php?branch=NAM
