"""
Fetch NAM forecast data for preset locations
Saves as static JSON files for GitHub Pages deployment
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Import from our existing app
sys.path.insert(0, str(Path(__file__).parent))
from app import NAMDataFetcher

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

def fetch_all_locations():
    """Fetch NAM data for all preset locations"""
    fetcher = NAMDataFetcher()

    # Create data directory
    data_dir = Path(__file__).parent / "docs" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "locations": [],
        "status": "success"
    }

    print(f"Fetching NAM data for {len(LOCATIONS)} locations...")

    success_count = 0
    for location in LOCATIONS:
        print(f"\nFetching data for {location['name']}...")
        try:
            data = fetcher.fetch_forecast_data(
                lat=location['lat'],
                lon=location['lon'],
                hours=72
            )

            # Add location name to data
            data['location_name'] = location['name']

            # Save individual location file
            filename = location['name'].lower().replace(', ', '-').replace(' ', '_') + '.json'
            filepath = data_dir / filename

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"✓ Saved {len(data['hourly_data'])} hours of data to {filename}")

            # Add to index
            results['locations'].append({
                "name": location['name'],
                "lat": location['lat'],
                "lon": location['lon'],
                "filename": filename,
                "data_points": len(data['hourly_data']),
                "model_run": data['model_run']
            })

            success_count += 1

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
    try:
        success = fetch_all_locations()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
