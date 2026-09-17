from datetime import datetime, timezone
from .database import db
import json

def get_utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), default='analyst')
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    state = db.Column(db.String(100), nullable=False, default='Maharashtra')
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    elevation_m = db.Column(db.Float, default=560.0)
    base_population = db.Column(db.Integer, default=3500000)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'lat': self.lat,
            'lon': self.lon,
            'elevation_m': self.elevation_m,
            'base_population': self.base_population
        }

class AQIData(db.Model):
    __tablename__ = 'aqi_data'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=get_utc_now)
    aqi = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    pm25 = db.Column(db.Float, nullable=False)
    pm10 = db.Column(db.Float, nullable=False)
    no2 = db.Column(db.Float, nullable=False)
    so2 = db.Column(db.Float, nullable=False)
    co = db.Column(db.Float, nullable=False)
    o3 = db.Column(db.Float, nullable=False)
    dominant_pollutant = db.Column(db.String(20), default='PM2.5')

    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'timestamp': self.timestamp.isoformat(),
            'aqi': self.aqi,
            'category': self.category,
            'pm25': self.pm25,
            'pm10': self.pm10,
            'no2': self.no2,
            'so2': self.so2,
            'co': self.co,
            'o3': self.o3,
            'dominant_pollutant': self.dominant_pollutant
        }

class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=get_utc_now)
    temperature_c = db.Column(db.Float, nullable=False)
    rainfall_mm = db.Column(db.Float, nullable=False)
    humidity_pct = db.Column(db.Float, nullable=False)
    wind_speed_kmh = db.Column(db.Float, default=12.0)
    water_availability_pct = db.Column(db.Float, default=80.0)
    power_availability_pct = db.Column(db.Float, default=100.0)

    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'timestamp': self.timestamp.isoformat(),
            'temperature_c': self.temperature_c,
            'rainfall_mm': self.rainfall_mm,
            'humidity_pct': self.humidity_pct,
            'wind_speed_kmh': self.wind_speed_kmh,
            'water_availability_pct': self.water_availability_pct,
            'power_availability_pct': self.power_availability_pct
        }

class Infrastructure(db.Model):
    __tablename__ = 'infrastructure'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Hospital, Shelter, School, Power Station, Water Facility
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, default=500)
    baseline_status = db.Column(db.String(50), default='Operational')
    criticality = db.Column(db.String(20), default='High')

    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'name': self.name,
            'type': self.type,
            'lat': self.lat,
            'lon': self.lon,
            'capacity': self.capacity,
            'baseline_status': self.baseline_status,
            'criticality': self.criticality
        }

class Road(db.Model):
    __tablename__ = 'roads'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    start_lat = db.Column(db.Float, nullable=False)
    start_lon = db.Column(db.Float, nullable=False)
    end_lat = db.Column(db.Float, nullable=False)
    end_lon = db.Column(db.Float, nullable=False)
    elevation_risk = db.Column(db.String(20), default='Medium')  # Low, Medium, High (low elevation = high flood risk)
    flood_threshold_mm = db.Column(db.Float, default=120.0)
    current_status = db.Column(db.String(50), default='Safe')
    is_emergency_route = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'name': self.name,
            'start_lat': self.start_lat,
            'start_lon': self.start_lon,
            'end_lat': self.end_lat,
            'end_lon': self.end_lon,
            'elevation_risk': self.elevation_risk,
            'flood_threshold_mm': self.flood_threshold_mm,
            'current_status': self.current_status,
            'is_emergency_route': self.is_emergency_route
        }

class Scenario(db.Model):
    __tablename__ = 'scenarios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    description = db.Column(db.Text, nullable=True)
    
    # Input Conditions
    rainfall_mm = db.Column(db.Float, nullable=False)
    temperature_c = db.Column(db.Float, nullable=False)
    aqi = db.Column(db.Integer, nullable=False)
    water_availability_pct = db.Column(db.Float, nullable=False)
    power_availability_pct = db.Column(db.Float, nullable=False)

    # Relationships
    results = db.relationship('ScenarioResult', backref='scenario', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location_name': self.location_name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'description': self.description,
            'inputs': {
                'rainfall_mm': self.rainfall_mm,
                'temperature_c': self.temperature_c,
                'aqi': self.aqi,
                'water_availability_pct': self.water_availability_pct,
                'power_availability_pct': self.power_availability_pct
            }
        }

class ScenarioResult(db.Model):
    __tablename__ = 'scenario_results'
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    
    # Risk Levels
    flood_risk = db.Column(db.String(20), nullable=False)
    heat_risk = db.Column(db.String(20), nullable=False)
    air_quality_risk = db.Column(db.String(20), nullable=False)
    water_risk = db.Column(db.String(20), nullable=False)
    overall_risk = db.Column(db.String(20), nullable=False)
    exposure_score = db.Column(db.Float, nullable=False)

    # Simulated Metrics
    population_exposed = db.Column(db.Integer, default=0)
    roads_at_risk = db.Column(db.Integer, default=0)
    hospitals_exposed = db.Column(db.Integer, default=0)
    
    # Full JSON payload for rendering map and details
    details_json = db.Column(db.Text, nullable=True)

    def to_dict(self):
        details = json.loads(self.details_json) if self.details_json else {}
        return {
            'id': self.id,
            'scenario_id': self.scenario_id,
            'flood_risk': self.flood_risk,
            'heat_risk': self.heat_risk,
            'air_quality_risk': self.air_quality_risk,
            'water_risk': self.water_risk,
            'overall_risk': self.overall_risk,
            'exposure_score': self.exposure_score,
            'population_exposed': self.population_exposed,
            'roads_at_risk': self.roads_at_risk,
            'hospitals_exposed': self.hospitals_exposed,
            'details': details
        }
