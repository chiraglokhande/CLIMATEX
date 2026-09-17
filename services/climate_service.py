import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'weather_sample.json')

class ClimateService:
    def __init__(self):
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_weather_by_location(self, location_name='Pune'):
        city_weather = self.data.get(location_name, self.data.get('Pune', {}))
        return {
            'location': location_name,
            'temperature_c': city_weather.get('temperature_c', 30.0),
            'rainfall_mm': city_weather.get('rainfall_mm', 100.0),
            'humidity_pct': city_weather.get('humidity_pct', 74.0),
            'wind_speed_kmh': city_weather.get('wind_speed_kmh', 14.5),
            'water_availability_pct': city_weather.get('water_availability_pct', 80.0),
            'power_availability_pct': city_weather.get('power_availability_pct', 100.0),
            'flood_risk_baseline': city_weather.get('flood_risk_baseline', 'Medium'),
            'heat_risk_baseline': city_weather.get('heat_risk_baseline', 'Low'),
            'water_risk_baseline': city_weather.get('water_risk_baseline', 'Low'),
            'temp_trend': city_weather.get('temp_trend', []),
            'rainfall_trend': city_weather.get('rainfall_trend', []),
            'dates': city_weather.get('dates', [])
        }

    def get_all_locations(self):
        return [
            {'name': 'Pune', 'lat': 18.5204, 'lon': 73.8567, 'elevation': 560},
            {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'elevation': 14},
            {'name': 'Nashik', 'lat': 19.9975, 'lon': 73.7898, 'elevation': 584},
            {'name': 'Nagpur', 'lat': 21.1458, 'lon': 79.0882, 'elevation': 310}
        ]
