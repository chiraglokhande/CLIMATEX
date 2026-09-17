import unittest
import json
from app import create_app
from models.database import db
from models.models import Scenario, Location

class ClimatexTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_pages_load(self):
        routes = [
            '/',
            '/about',
            '/dashboard',
            '/aqi',
            '/aqi-solutions',
            '/simulator',
            '/results?location=Pune&rainfall=150&temperature=33&aqi=185&water=70&power=100',
            '/map',
            '/reports'
        ]
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Route {route} failed with status {response.status_code}")

    def test_weather_api(self):
        res = self.client.get('/api/weather/Pune')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('weather', data)
        self.assertIn('aqi', data)
        self.assertIn('risk', data)

    def test_aqi_api(self):
        res = self.client.get('/api/aqi/Pune')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('aqi_data', data)
        self.assertIn('causes', data)

    def test_simulate_api(self):
        payload = {
            "location": "Pune",
            "rainfall": 150,
            "temperature": 33,
            "aqi": 185,
            "water_availability": 70,
            "power_availability": 100
        }
        res = self.client.post('/api/simulate', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['simulation']['simulated']['risk']['flood_risk'], 'HIGH')
        self.assertEqual(data['simulation']['simulated']['risk']['air_quality_risk'], 'HIGH')
        self.assertEqual(data['simulation']['simulated']['risk']['overall_risk'], 'HIGH')

    def test_scenario_save_and_pdf(self):
        # Save scenario
        payload = {
            "name": "Automated Test Scenario",
            "location": "Pune",
            "rainfall": 160,
            "temperature": 32,
            "aqi": 190,
            "water_availability": 75,
            "power_availability": 90,
            "description": "Test description"
        }
        res = self.client.post('/api/scenarios/save', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        scenario_id = data['scenario_id']

        # Download PDF
        pdf_res = self.client.get(f'/reports/download/{scenario_id}')
        self.assertEqual(pdf_res.status_code, 200)
        self.assertEqual(pdf_res.mimetype, 'application/pdf')

    def test_map_data_api(self):
        res = self.client.get('/api/map-data?location=Pune')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('roads', data)
        self.assertIn('infrastructure', data)
        self.assertIn('risk_zones', data)

if __name__ == '__main__':
    unittest.main()
