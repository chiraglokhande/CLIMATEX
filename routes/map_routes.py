from flask import Blueprint, render_template, jsonify, request
from services.climate_service import ClimateService
from services.simulation_engine import SimulationEngine
from services.aqi_service import AQIService

map_bp = Blueprint('map', __name__)
climate_service = ClimateService()
simulation_engine = SimulationEngine()
aqi_service = AQIService()

@map_bp.route('/map')
def interactive_map():
    location = request.args.get('location', 'Pune')
    locations = climate_service.get_all_locations()
    return render_template('map.html', location=location, locations=locations)

@map_bp.route('/api/map-data')
def get_map_data():
    location = request.args.get('location', 'Pune')
    rainfall = request.args.get('rainfall', type=float)
    temp = request.args.get('temperature', type=float)
    aqi = request.args.get('aqi', type=int)
    water = request.args.get('water', type=float)
    power = request.args.get('power', type=float)

    # If simulation parameters are passed, return the simulated map features
    if rainfall is not None or aqi is not None or temp is not None:
        rf = rainfall if rainfall is not None else 100.0
        tp = temp if temp is not None else 30.0
        aq = aqi if aqi is not None else 120
        wa = water if water is not None else 80.0
        pw = power if power is not None else 100.0
        sim = simulation_engine.simulate(location, rf, tp, aq, wa, pw)
        return jsonify({
            'location': location,
            'simulated': True,
            'roads': sim['roads'],
            'infrastructure': sim['infrastructure'],
            'risk_zones': sim['risk_zones'],
            'risk': sim['simulated']['risk']
        })

    # Default baseline map data
    weather = climate_service.get_weather_by_location(location)
    aqi_data = aqi_service.get_aqi_by_location(location)
    sim = simulation_engine.simulate(
        location,
        weather['rainfall_mm'],
        weather['temperature_c'],
        aqi_data['aqi'],
        weather['water_availability_pct'],
        weather['power_availability_pct']
    )

    return jsonify({
        'location': location,
        'simulated': False,
        'hotspots': aqi_data.get('hotspots', []),
        'roads': sim['roads'],
        'infrastructure': sim['infrastructure'],
        'risk_zones': sim['risk_zones'],
        'risk': sim['baseline']['risk']
    })
