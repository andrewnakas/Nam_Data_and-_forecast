"""
Simplified data fetcher using NOAA's weather.gov API
More reliable than OpenDAP/NOMADS servers
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
import time

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

def fetch_weather_data(lat, lon):
    """Fetch weather data from NOAA weather.gov API"""
    try:
        # Get forecast office and grid coordinates
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        headers = {'User-Agent': 'NAM-Weather-App (github.com/andrewnakas)'}

        response = requests.get(points_url, headers=headers, timeout=10)
        response.raise_for_status()
        points_data = response.json()

        # Get hourly forecast
        forecast_url = points_data['properties']['forecastHourly']
        time.sleep(0.5)  # Rate limiting

        response = requests.get(forecast_url, headers=headers, timeout=10)
        response.raise_for_status()
        forecast_data = response.json()

        return forecast_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def convert_to_app_format(location, forecast_data):
    """Convert weather.gov format to our app format"""
    if not forecast_data:
        return None

    periods = forecast_data.get('properties', {}).get('periods', [])
    if not periods:
        return None

    # Convert to our format
    result = {
        'location_name': location['name'],
        'location': {
            'lat': location['lat'],
            'lon': location['lon']
        },
        'model_run': datetime.now(timezone.utc).isoformat(),
        'hourly_data': []
    }

    for i, period in enumerate(periods[:72]):  # Up to 72 hours
        # Parse wind speed (format: "10 mph" or "5 to 10 mph")
        wind_str = period.get('windSpeed', '0 mph')
        try:
            wind_mph = float(wind_str.split()[0])
            wind_ms = wind_mph * 0.44704  # mph to m/s
        except:
            wind_mph = 0
            wind_ms = 0

        # Parse wind direction
        wind_dir_str = period.get('windDirection', 'N')
        wind_dir_map = {
            'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
            'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
            'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
            'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
        }
        wind_dir = wind_dir_map.get(wind_dir_str, 0)

        # Temperature (F to C)
        temp_f = period.get('temperature', 70)
        temp_c = (temp_f - 32) * 5/9

        # Precipitation probability
        precip_prob = period.get('probabilityOfPrecipitation', {}).get('value', 0) or 0
        rh = period.get('relativeHumidity', {}).get('value', 50) or 50

        # Estimate atmospheric profile based on standard atmosphere
        # Temperature decreases ~6.5°C per km (troposphere lapse rate)
        # Wind generally increases with altitude
        hourly_entry = {
            'valid_time': period.get('startTime', ''),
            'forecast_hour': i,
            'surface': {
                'temperature_2m': temp_c,
                'temperature_surface': temp_c,
                'wind_speed_10m': wind_ms,
                'wind_direction_10m': wind_dir,
                'wind_u_10m': -wind_ms * 0.866,  # Approximation
                'wind_v_10m': -wind_ms * 0.5,
                'precipitation_rate': precip_prob / 100.0,  # Rough estimate
            },
            'levels': {
                '1000mb': {
                    'temperature': temp_c - 0.5,
                    'wind_speed': wind_ms * 1.0,
                    'wind_direction': wind_dir,
                    'relative_humidity': rh,
                    'height': 110
                },
                '925mb': {
                    'temperature': temp_c - 4,
                    'wind_speed': wind_ms * 1.1,
                    'wind_direction': wind_dir + 5,
                    'relative_humidity': max(rh - 5, 20),
                    'height': 762
                },
                '850mb': {
                    'temperature': temp_c - 9,
                    'wind_speed': wind_ms * 1.2,
                    'wind_direction': wind_dir + 10,
                    'relative_humidity': max(rh - 10, 15),
                    'height': 1457
                },
                '700mb': {
                    'temperature': temp_c - 19,
                    'wind_speed': wind_ms * 1.4,
                    'wind_direction': wind_dir + 15,
                    'relative_humidity': max(rh - 20, 10),
                    'height': 3012
                },
                '500mb': {
                    'temperature': temp_c - 35,
                    'wind_speed': wind_ms * 1.8,
                    'wind_direction': wind_dir + 25,
                    'relative_humidity': max(rh - 35, 5),
                    'height': 5574
                },
                '300mb': {
                    'temperature': temp_c - 55,
                    'wind_speed': wind_ms * 2.5,
                    'wind_direction': wind_dir + 40,
                    'relative_humidity': max(rh - 50, 2),
                    'height': 9164
                },
                '250mb': {
                    'temperature': temp_c - 60,
                    'wind_speed': wind_ms * 3.0,
                    'wind_direction': wind_dir + 50,
                    'relative_humidity': max(rh - 55, 1),
                    'height': 10363
                }
            }
        }

        result['hourly_data'].append(hourly_entry)

    return result

def fetch_all_locations():
    """Fetch weather data for all preset locations"""
    data_dir = Path(__file__).parent / "docs" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "locations": [],
        "status": "success"
    }

    print(f"Fetching weather data for {len(LOCATIONS)} locations using NOAA weather.gov API...")

    success_count = 0
    for location in LOCATIONS:
        print(f"\nFetching data for {location['name']}...")
        try:
            forecast_data = fetch_weather_data(location['lat'], location['lon'])

            if forecast_data:
                app_data = convert_to_app_format(location, forecast_data)

                if app_data:
                    # Save individual location file
                    filename = location['name'].lower().replace(', ', '-').replace(' ', '_') + '.json'
                    filepath = data_dir / filename

                    with open(filepath, 'w') as f:
                        json.dump(app_data, f, indent=2)

                    print(f"✓ Saved {len(app_data['hourly_data'])} hours of data to {filename}")

                    results['locations'].append({
                        "name": location['name'],
                        "lat": location['lat'],
                        "lon": location['lon'],
                        "filename": filename,
                        "data_points": len(app_data['hourly_data']),
                        "model_run": app_data['model_run']
                    })

                    success_count += 1
                else:
                    raise Exception("Failed to convert data")
            else:
                raise Exception("Failed to fetch forecast data")

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
