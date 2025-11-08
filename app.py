"""
NAM Weather Forecast Backend API
Fetches NAM (North American Mesoscale) forecast data from NOAA
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import xarray as xr
import numpy as np
from siphon.catalog import TDSCatalog
import json

app = Flask(__name__)
CORS(app)

# NOAA NOMADS THREDDS Data Server
THREDDS_URL = "https://thredds.ucar.edu/thredds/catalog/grib/NCEP/NAM/CONUS_12km/latest.xml"

class NAMDataFetcher:
    """Fetch and process NAM forecast data"""

    def __init__(self):
        self.base_url = "https://nomads.ncep.noaa.gov/dods/nam"

    def get_latest_dataset(self):
        """Get the latest NAM dataset URL"""
        try:
            # Use NOMADS OpenDAP server
            now = datetime.utcnow()
            # NAM runs at 00, 06, 12, 18 UTC
            run_hours = [0, 6, 12, 18]

            # Find the most recent model run
            for hours_back in range(24):
                check_time = now - timedelta(hours=hours_back)
                for run_hour in reversed(run_hours):
                    if check_time.hour >= run_hour:
                        model_time = check_time.replace(hour=run_hour, minute=0, second=0, microsecond=0)
                        break

                date_str = model_time.strftime("%Y%m%d")
                run_str = f"{model_time.hour:02d}"

                # Try to access the dataset
                dataset_url = f"{self.base_url}/nam{date_str}/nam_conusnest_{run_str}z"

                try:
                    # Test if dataset exists
                    test_ds = xr.open_dataset(dataset_url, engine='netcdf4')
                    test_ds.close()
                    return dataset_url, model_time
                except:
                    continue

            return None, None
        except Exception as e:
            print(f"Error getting latest dataset: {e}")
            return None, None

    def fetch_forecast_data(self, lat, lon, hours=72):
        """
        Fetch NAM forecast data for a specific location

        Args:
            lat: Latitude
            lon: Longitude
            hours: Forecast hours (default 72 for 3 days)
        """
        try:
            dataset_url, model_time = self.get_latest_dataset()

            if not dataset_url:
                raise Exception("Could not find valid NAM dataset")

            print(f"Opening dataset: {dataset_url}")
            ds = xr.open_dataset(dataset_url, engine='netcdf4')

            # Convert longitude to 0-360 if needed
            if lon < 0:
                lon = lon + 360

            # Select the closest grid point
            ds_point = ds.sel(lat=lat, lon=lon, method='nearest')

            # Get time range (next 72 hours, hourly)
            max_time_idx = min(hours, len(ds_point.time))
            ds_point = ds_point.isel(time=slice(0, max_time_idx))

            # Pressure levels in millibars
            pressure_levels = [1000, 925, 850, 700, 500, 300, 250]

            # Extract data
            forecast_data = {
                'model_run': model_time.isoformat(),
                'location': {
                    'lat': float(lat),
                    'lon': float(lon - 360 if lon > 180 else lon)
                },
                'hourly_data': []
            }

            # Extract variables
            for time_idx in range(max_time_idx):
                time_point = ds_point.isel(time=time_idx)
                valid_time = time_point.time.values

                hourly_entry = {
                    'valid_time': str(valid_time),
                    'forecast_hour': time_idx,
                    'surface': {},
                    'levels': {}
                }

                # Surface variables
                if 'tmp2m' in ds_point:
                    hourly_entry['surface']['temperature_2m'] = float(time_point.tmp2m.values - 273.15)  # K to C
                if 'tmpsfc' in ds_point:
                    hourly_entry['surface']['temperature_surface'] = float(time_point.tmpsfc.values - 273.15)

                # Precipitation
                if 'apcpsfc' in ds_point:
                    hourly_entry['surface']['precipitation'] = float(time_point.apcpsfc.values)
                elif 'pratesfc' in ds_point:
                    hourly_entry['surface']['precipitation_rate'] = float(time_point.pratesfc.values)

                # Wind at surface/10m
                if 'ugrd10m' in ds_point and 'vgrd10m' in ds_point:
                    u = float(time_point.ugrd10m.values)
                    v = float(time_point.vgrd10m.values)
                    speed = np.sqrt(u**2 + v**2)
                    direction = (270 - np.degrees(np.arctan2(v, u))) % 360
                    hourly_entry['surface']['wind_speed_10m'] = speed
                    hourly_entry['surface']['wind_direction_10m'] = direction
                    hourly_entry['surface']['wind_u_10m'] = u
                    hourly_entry['surface']['wind_v_10m'] = v

                # Pressure level data
                if 'lev' in ds_point.dims:
                    for pressure in pressure_levels:
                        try:
                            level_data = time_point.sel(lev=pressure, method='nearest')
                            level_info = {}

                            # Temperature at level
                            if 'tmpprs' in ds_point:
                                level_info['temperature'] = float(level_data.tmpprs.values - 273.15)

                            # Wind at level
                            if 'ugrdprs' in ds_point and 'vgrdprs' in ds_point:
                                u = float(level_data.ugrdprs.values)
                                v = float(level_data.vgrdprs.values)
                                speed = np.sqrt(u**2 + v**2)
                                direction = (270 - np.degrees(np.arctan2(v, u))) % 360
                                level_info['wind_speed'] = speed
                                level_info['wind_direction'] = direction
                                level_info['wind_u'] = u
                                level_info['wind_v'] = v

                            # Relative humidity
                            if 'rhprs' in ds_point:
                                level_info['relative_humidity'] = float(level_data.rhprs.values)

                            # Geopotential height
                            if 'hgtprs' in ds_point:
                                level_info['height'] = float(level_data.hgtprs.values)

                            if level_info:
                                hourly_entry['levels'][f"{pressure}mb"] = level_info
                        except Exception as e:
                            print(f"Error processing {pressure}mb: {e}")
                            continue

                forecast_data['hourly_data'].append(hourly_entry)

            ds.close()
            return forecast_data

        except Exception as e:
            print(f"Error fetching forecast data: {e}")
            raise

# Initialize fetcher
fetcher = NAMDataFetcher()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    """
    Get NAM forecast data for a location
    Query params: lat, lon, hours (optional, default 72)
    """
    try:
        lat = float(request.args.get('lat', 40.7128))  # Default to NYC
        lon = float(request.args.get('lon', -74.0060))
        hours = int(request.args.get('hours', 72))

        # Validate inputs
        if not (-90 <= lat <= 90):
            return jsonify({'error': 'Invalid latitude'}), 400
        if not (-180 <= lon <= 180):
            return jsonify({'error': 'Invalid longitude'}), 400
        if not (1 <= hours <= 84):
            return jsonify({'error': 'Hours must be between 1 and 84'}), 400

        data = fetcher.fetch_forecast_data(lat, lon, hours)
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Check if NAM data is available"""
    try:
        dataset_url, model_time = fetcher.get_latest_dataset()
        if dataset_url:
            return jsonify({
                'status': 'available',
                'latest_run': model_time.isoformat(),
                'dataset_url': dataset_url
            })
        else:
            return jsonify({
                'status': 'unavailable',
                'message': 'Could not find valid NAM dataset'
            }), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
