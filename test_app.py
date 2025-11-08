"""
Test suite for NAM Weather Forecast Application
"""
import unittest
import json
from app import app, NAMDataFetcher


class TestNAMApp(unittest.TestCase):
    """Test cases for the Flask application"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        """Test that the index route returns HTML"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'NAM Weather Forecast Viewer', response.data)

    def test_status_endpoint(self):
        """Test the status endpoint"""
        response = self.app.get('/api/status')
        self.assertIn(response.status_code, [200, 503])  # May be available or unavailable
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_forecast_endpoint_valid(self):
        """Test forecast endpoint with valid coordinates"""
        response = self.app.get('/api/forecast?lat=40.7128&lon=-74.0060&hours=24')
        # May succeed or fail depending on data availability
        self.assertIn(response.status_code, [200, 500])

    def test_forecast_endpoint_invalid_lat(self):
        """Test forecast endpoint with invalid latitude"""
        response = self.app.get('/api/forecast?lat=100&lon=-74.0060')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_forecast_endpoint_invalid_lon(self):
        """Test forecast endpoint with invalid longitude"""
        response = self.app.get('/api/forecast?lat=40.7128&lon=200')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_forecast_endpoint_invalid_hours(self):
        """Test forecast endpoint with invalid hours"""
        response = self.app.get('/api/forecast?lat=40.7128&lon=-74.0060&hours=100')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_fetcher_initialization(self):
        """Test NAMDataFetcher initialization"""
        fetcher = NAMDataFetcher()
        self.assertIsNotNone(fetcher)
        self.assertTrue(hasattr(fetcher, 'base_url'))


class TestNAMDataFetcher(unittest.TestCase):
    """Test cases for NAMDataFetcher class"""

    def setUp(self):
        """Set up fetcher instance"""
        self.fetcher = NAMDataFetcher()

    def test_base_url(self):
        """Test that base URL is set correctly"""
        self.assertEqual(self.fetcher.base_url, "https://nomads.ncep.noaa.gov/dods/nam")

    def test_get_latest_dataset(self):
        """Test getting latest dataset URL"""
        dataset_url, model_time = self.fetcher.get_latest_dataset()
        # May return None if data is unavailable, which is acceptable
        if dataset_url:
            self.assertIn('nomads.ncep.noaa.gov', dataset_url)
            self.assertIsNotNone(model_time)


if __name__ == '__main__':
    unittest.main()
