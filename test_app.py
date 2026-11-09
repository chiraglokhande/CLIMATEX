import unittest
import json
from app import create_app
from models.database import db
from models.models import Scenario, Location, User

class ClimatexTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_unauthenticated_access_is_blocked(self):
        """Verify that without login, NO feature can be accessed and redirects to login."""
        protected_routes = [
            '/dashboard',
            '/aqi',
            '/aqi-solutions',
            '/simulator',
            '/results?location=Pune&rainfall=150&temperature=33&aqi=185&water=70&power=100',
            '/map',
            '/reports'
        ]
        for route in protected_routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 302, f"Unauthenticated access to {route} was not blocked!")
            self.assertIn('/login', res.headers.get('Location', ''))

        # APIs must return 401 Unauthorized
        api_res = self.client.get('/api/weather/Pune')
        self.assertEqual(api_res.status_code, 401)
        self.assertEqual(api_res.get_json()['status'], 'error')

    def test_auth_gateway_page_content(self):
        """Verify that first page shows only Login and Register, without feature links."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        # Options present (strictly Login and Register, no slashes)
        self.assertIn(b'Login', res.data)
        self.assertIn(b'Register', res.data)
        self.assertNotIn(b'256-bit Encrypted', res.data)
        self.assertNotIn(b'Professional Role', res.data)
        # Other features must NOT be in the navigation
        self.assertNotIn(b'Run Scenario', res.data)
        self.assertNotIn(b'Explore Platform Overview', res.data)
        self.assertNotIn(b'Continue as Guest', res.data)

    def test_login_unlocks_all_features(self):
        """Verify that logging in unlocks all platform features."""
        # 1. Log in using instant demo login
        demo_res = self.client.post('/demo-login', content_type='application/json')
        self.assertEqual(demo_res.status_code, 200)
        self.assertEqual(demo_res.get_json()['status'], 'success')

        # 2. Now all feature pages should return 200 OK
        feature_routes = [
            '/dashboard',
            '/aqi',
            '/aqi-solutions',
            '/simulator',
            '/results?location=Pune&rainfall=150&temperature=33&aqi=185&water=70&power=100',
            '/map',
            '/reports',
            '/home',
            '/about'
        ]
        for route in feature_routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Authenticated route {route} failed")

        # 3. Weather API
        w_res = self.client.get('/api/weather/Pune')
        self.assertEqual(w_res.status_code, 200)
        w_data = w_res.get_json()
        self.assertIn('weather', w_data)
        self.assertIn('aqi', w_data)

        # 4. Simulate API
        sim_payload = {
            "location": "Pune",
            "rainfall": 150,
            "temperature": 33,
            "aqi": 185,
            "water_availability": 70,
            "power_availability": 100
        }
        sim_res = self.client.post('/api/simulate', data=json.dumps(sim_payload), content_type='application/json')
        self.assertEqual(sim_res.status_code, 200)

        # 5. Logout locks features again
        logout_res = self.client.get('/logout')
        self.assertEqual(logout_res.status_code, 302)

        locked_res = self.client.get('/dashboard')
        self.assertEqual(locked_res.status_code, 302)

    def test_registration_and_db_persistence(self):
        """Test full user registration cycle and persistence."""
        import time
        ts = int(time.time())
        uname = f"officer_{ts}"
        email = f"officer_{ts}@pune.gov.in"
        payload = {
            'username': uname,
            'email': email,
            'full_name': 'Rohan Deshmukh',
            'role': 'Municipal Disaster Coordinator',
            'password': 'SecureOfficerPass2026!',
            'confirm_password': 'SecureOfficerPass2026!'
        }
        res = self.client.post('/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['status'], 'success')

        # Duplicate username should be rejected
        dup_res = self.client.post('/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(dup_res.status_code, 400)

        # Login with registered user
        login_res = self.client.post('/login', data=json.dumps({
            'identifier': uname,
            'password': 'SecureOfficerPass2026!'
        }), content_type='application/json')
        self.assertEqual(login_res.status_code, 200)
        self.assertEqual(login_res.get_json()['status'], 'success')

if __name__ == '__main__':
    unittest.main()
