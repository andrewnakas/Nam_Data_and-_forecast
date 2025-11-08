"""
NAM Model Data Fetcher using NOMADS GRIB Filter
Gets actual NAM forecast data with pressure levels
"""

import json
import requests
import xarray as xr
import cfgrib
from datetime import datetime, timezone, timedelta
from pathlib import Path
import time
import tempfile
import os

# Preset locations to fetch data for
LOCATIONS = [
    {"name": "New York, NY", "lat": 40.7128, "lon": -74.0060},
    {"name": "Los Angeles, CA", "lat": 34.0522, "lon": -118.2437},
    {"name": "Chicago, IL", "lat": 41.8781, "lon": -87.6298},
    {"name": "Houston, TX", "lat": 29.7604, "lon": -95.3698},
    {"name": "Phoenix, AZ", "lat": 33.4484, "lon": -112.0740},
    {"name": "Philadelphia, PA", "lat": 39.9526, "lon": -75.1652},
    {"name": "San Antonio, TX", "lat": 29.4241, "lon": -98.4936},
    {"name": "San Diego, CA", "lat": 32.7157, "lon": -117.1611},
    {"name": "Dallas, TX", "lat": 32.7767, "lon": -96.7970},
    {"name": "Denver, CO", "lat": 39.7392, "lon": -104.9903},
    {"name": "Seattle, WA", "lat": 47.6062, "lon": -122.3321},
    {"name": "Miami, FL", "lat": 25.7617, "lon": -80.1918},
    {"name": "Atlanta, GA", "lat": 33.7490, "lon": -84.3880},
    {"name": "Boston, MA", "lat": 42.3601, "lon": -71.0589},
    {"name": "Detroit, MI", "lat": 42.3314, "lon": -83.0458},
]

# Pressure levels to fetch
PRESSURE_LEVELS = [1000, 925, 850, 700, 500, 300, 250]

def get_latest_nam_run():
    """Determine the latest available NAM model run"""
    now = datetime.now(timezone.utc)

    # NAM runs at 00Z, 06Z, 12Z, 18Z
    # Use the most recent completed run (subtract 4 hours for processing time)
    run_time = now - timedelta(hours=4)
    cycle_hour = (run_time.hour // 6) * 6

    run_date = run_time.replace(hour=cycle_hour, minute=0, second=0, microsecond=0)

    return run_date

def download_nam_grib(run_date, forecast_hour, region_box):
    """
    Download NAM GRIB2 data for a specific forecast hour and region

    Args:
        run_date: datetime of model run
        forecast_hour: forecast hour (0-84)
        region_box: dict with leftlon, rightlon, toplat, bottomlat

    Returns:
        Path to downloaded GRIB2 file or None
    """
    date_str = run_date.strftime("%Y%m%d")
    cycle = run_date.strftime("%H")
    fhour = f"{forecast_hour:02d}"

    # NAM GRIB filter URL
    base_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_nam.pl"

    # Build parameters
    params = {
        'file': f'nam.t{cycle}z.awphys{fhour}.tm00.grib2',
        'dir': f'/nam.{date_str}',

        # Surface variables
        'var_TMP': 'on',      # Temperature
        'var_UGRD': 'on',     # U-wind component
        'var_VGRD': 'on',     # V-wind component
        'var_RH': 'on',       # Relative humidity
        'var_PRMSL': 'on',    # Pressure at MSL

        # Surface levels
        'lev_2_m_above_ground': 'on',
        'lev_10_m_above_ground': 'on',
        'lev_mean_sea_level': 'on',
        'lev_surface': 'on',
    }

    # Add pressure levels
    for level in PRESSURE_LEVELS:
        params[f'lev_{level}_mb'] = 'on'

    # Add region subset
    params.update({
        'subregion': '',
        'leftlon': str(region_box['leftlon']),
        'rightlon': str(region_box['rightlon']),
        'toplat': str(region_box['toplat']),
        'bottomlat': str(region_box['bottomlat'])
    })

    try:
        print(f"  Downloading forecast hour {fhour}...")
        response = requests.get(base_url, params=params, timeout=120)
        response.raise_for_status()

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.grib2')
        temp_file.write(response.content)
        temp_file.close()

        print(f"    Downloaded {len(response.content)} bytes")
        return temp_file.name

    except Exception as e:
        print(f"  Error downloading hour {fhour}: {e}")
        return None

def extract_point_data(grib_file, lat, lon, forecast_hour, valid_time):
    """Extract data for a specific lat/lon from GRIB file"""
    try:
        # Open with cfgrib - need to handle multiple messages
        datasets = []

        # Try to open all filter_by_keys combinations
        for filter_key in [
            {},  # All data
            {'typeOfLevel': 'isobaricInhPa'},  # Pressure levels
            {'typeOfLevel': 'heightAboveGround'},  # Height levels
            {'typeOfLevel': 'meanSea'},  # MSL
            {'typeOfLevel': 'surface'},  # Surface
        ]:
            try:
                ds = xr.open_dataset(
                    grib_file,
                    engine='cfgrib',
                    backend_kwargs={
                        'filter_by_keys': filter_key,
                        'errors': 'ignore'
                    }
                )
                datasets.append(ds)
            except:
                continue

        if not datasets:
            print(f"    Warning: Could not open GRIB file")
            return None

        # Extract data at the point
        result = {
            'valid_time': valid_time.isoformat(),
            'forecast_hour': forecast_hour,
            'surface': {},
            'levels': {}
        }

        # Process each dataset
        for ds in datasets:
            # Find nearest point using lat/lon coordinates
            if 'latitude' in ds.coords and 'longitude' in ds.coords:
                import numpy as np
                import math

                # Get lat/lon arrays
                lats = ds.latitude.values
                lons = ds.longitude.values

                # Convert target longitude to 0-360 if needed
                target_lon = lon % 360

                # Find nearest grid point
                if lats.ndim == 2:
                    # 2D coordinates
                    dist = np.sqrt((lats - lat)**2 + (lons - target_lon)**2)
                    min_idx = np.unravel_index(dist.argmin(), dist.shape)
                    if 'y' in ds.dims and 'x' in ds.dims:
                        point = ds.isel(y=min_idx[0], x=min_idx[1])
                    else:
                        continue
                elif lats.ndim == 1:
                    # 1D coordinates
                    lat_idx = abs(lats - lat).argmin()
                    lon_idx = abs(lons - target_lon).argmin()
                    point = ds.isel(y=lat_idx, x=lon_idx) if 'y' in ds.dims else ds.isel(latitude=lat_idx, longitude=lon_idx)
                else:
                    continue

                # Extract surface variables (no pressure dimension)
                if 't2m' in point.variables:
                    temp_k = float(point['t2m'].values)
                    result['surface']['temperature_2m'] = temp_k - 273.15
                    result['surface']['temperature_surface'] = temp_k - 273.15

                if 'u10' in point.variables:
                    result['surface']['wind_u_10m'] = float(point['u10'].values)
                if 'v10' in point.variables:
                    result['surface']['wind_v_10m'] = float(point['v10'].values)

                # Calculate surface wind speed and direction
                if 'wind_u_10m' in result['surface'] and 'wind_v_10m' in result['surface']:
                    u = result['surface']['wind_u_10m']
                    v = result['surface']['wind_v_10m']
                    result['surface']['wind_speed_10m'] = (u**2 + v**2)**0.5
                    result['surface']['wind_direction_10m'] = (270 - math.atan2(v, u) * 180/math.pi) % 360

                # Extract pressure level data (has pressure dimension)
                if 'isobaricInhPa' in point.coords:
                    for level in PRESSURE_LEVELS:
                        try:
                            level_data = point.sel(isobaricInhPa=level)
                            level_key = f"{level}mb"
                            result['levels'][level_key] = {}

                            if 't' in level_data.variables:
                                temp_k = float(level_data['t'].values)
                                result['levels'][level_key]['temperature'] = temp_k - 273.15

                            if 'u' in level_data.variables:
                                u = float(level_data['u'].values)
                                result['levels'][level_key]['wind_u'] = u

                            if 'v' in level_data.variables:
                                v = float(level_data['v'].values)
                                result['levels'][level_key]['wind_v'] = v

                            if 'r' in level_data.variables:
                                result['levels'][level_key]['relative_humidity'] = float(level_data['r'].values)

                            # Calculate wind speed and direction
                            if 'wind_u' in result['levels'][level_key] and 'wind_v' in result['levels'][level_key]:
                                u = result['levels'][level_key]['wind_u']
                                v = result['levels'][level_key]['wind_v']
                                result['levels'][level_key]['wind_speed'] = (u**2 + v**2)**0.5
                                result['levels'][level_key]['wind_direction'] = (270 - math.atan2(v, u) * 180/math.pi) % 360

                        except Exception as e:
                            # Level might not be available
                            continue

            ds.close()

        return result

    except Exception as e:
        print(f"    Error extracting point data: {e}")
        return None

def fetch_nam_for_location(location, run_date):
    """Fetch NAM data for a specific location"""
    print(f"\nFetching NAM data for {location['name']}...")

    # Define region box around the location (±5 degrees)
    region_box = {
        'leftlon': location['lon'] - 5,
        'rightlon': location['lon'] + 5,
        'toplat': location['lat'] + 5,
        'bottomlat': location['lat'] - 5
    }

    result = {
        'location_name': location['name'],
        'location': {
            'lat': location['lat'],
            'lon': location['lon']
        },
        'model': 'NAM',
        'model_run': run_date.isoformat(),
        'hourly_data': []
    }

    # Download forecast hours (NAM goes out to 84 hours, but we'll get first 84)
    # For efficiency, get every 1 hour for first 36, then every 3 hours
    forecast_hours = list(range(0, 37, 1)) + list(range(39, 85, 3))

    for fhour in forecast_hours:
        valid_time = run_date + timedelta(hours=fhour)

        # Download GRIB for this hour
        grib_file = download_nam_grib(run_date, fhour, region_box)

        if grib_file:
            # Extract data for this location
            hourly_data = extract_point_data(grib_file, location['lat'], location['lon'], fhour, valid_time)

            if hourly_data:
                result['hourly_data'].append(hourly_data)

            # Clean up GRIB file
            try:
                os.unlink(grib_file)
            except:
                pass

            # Rate limiting - 10 seconds between requests
            if fhour < forecast_hours[-1]:
                print(f"    Waiting 10s (rate limiting)...")
                time.sleep(10)

    return result

def fetch_all_locations():
    """Fetch NAM data for all locations"""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    run_date = get_latest_nam_run()

    print(f"="*60)
    print(f"NAM Model Data Fetcher")
    print(f"Model Run: {run_date.strftime('%Y-%m-%d %HZ')}")
    print(f"Fetching {len(LOCATIONS)} locations")
    print(f"="*60)

    results = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "model": "NAM",
        "model_run": run_date.isoformat(),
        "locations": [],
        "status": "success"
    }

    success_count = 0
    for location in LOCATIONS:
        try:
            location_data = fetch_nam_for_location(location, run_date)

            if location_data and len(location_data['hourly_data']) > 0:
                # Save individual location file
                filename = location['name'].lower().replace(', ', '-').replace(' ', '_') + '.json'
                filepath = data_dir / filename

                with open(filepath, 'w') as f:
                    json.dump(location_data, f, indent=2)

                print(f"✓ Saved {len(location_data['hourly_data'])} hours to {filename}")

                results['locations'].append({
                    "name": location['name'],
                    "lat": location['lat'],
                    "lon": location['lon'],
                    "filename": filename,
                    "data_points": len(location_data['hourly_data']),
                    "model_run": location_data['model_run']
                })

                success_count += 1
            else:
                raise Exception("No data retrieved")

        except Exception as e:
            print(f"✗ Error fetching {location['name']}: {e}")
            results['locations'].append({
                "name": location['name'],
                "lat": location['lat'],
                "lon": location['lon'],
                "error": str(e)
            })

    # Save index file
    index_path = data_dir / "index.json"
    with open(index_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Fetch complete: {success_count}/{len(LOCATIONS)} locations successful")
    print(f"Index saved to {index_path}")
    print(f"{'='*60}")

    return success_count > 0

if __name__ == '__main__':
    import sys
    try:
        success = fetch_all_locations()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
