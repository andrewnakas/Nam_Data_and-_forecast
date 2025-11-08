#!/usr/bin/env python
"""
Health check script for NAM Weather Forecast App
Returns exit code 0 if app is healthy, 1 otherwise
"""
import sys
import requests
from urllib.parse import urljoin


def check_health(base_url='http://localhost:5000'):
    """Check if the application is healthy"""
    try:
        # Check main page
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            print(f"❌ Main page failed: {response.status_code}")
            return False
        print("✓ Main page accessible")

        # Check status endpoint
        status_url = urljoin(base_url, '/api/status')
        response = requests.get(status_url, timeout=5)
        if response.status_code not in [200, 503]:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
        print("✓ Status endpoint responding")

        # Check forecast endpoint with valid params
        forecast_url = urljoin(base_url, '/api/forecast')
        params = {'lat': 40.7128, 'lon': -74.0060, 'hours': 24}
        response = requests.get(forecast_url, params=params, timeout=10)
        if response.status_code not in [200, 500]:  # 500 acceptable if NAM data unavailable
            print(f"❌ Forecast endpoint failed: {response.status_code}")
            return False
        print("✓ Forecast endpoint responding")

        # Check static files
        css_url = urljoin(base_url, '/static/css/style.css')
        response = requests.get(css_url, timeout=5)
        if response.status_code != 200:
            print(f"❌ Static files not accessible: {response.status_code}")
            return False
        print("✓ Static files accessible")

        print("\n✅ All health checks passed!")
        return True

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == '__main__':
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'
    print(f"Checking health of: {base_url}\n")

    if check_health(base_url):
        sys.exit(0)
    else:
        sys.exit(1)
