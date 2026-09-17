from flask import Blueprint, render_template, jsonify, request
from services.climate_service import ClimateService
from services.aqi_service import AQIService
from services.risk_engine import RiskEngine

dashboard_bp = Blueprint('dashboard', __name__)
climate_service = ClimateService()
aqi_service = AQIService()
risk_engine = RiskEngine()

@dashboard_bp.route('/dashboard')
def dashboard():
    location = request.args.get('location', 'Pune')
    weather = climate_service.get_weather_by_location(location)
    aqi_data = aqi_service.get_aqi_by_location(location)
    
    # Calculate baseline multi-factor risks
    current_risk = risk_engine.compute_multi_factor_risk(
        weather['rainfall_mm'],
        weather['temperature_c'],
        aqi_data['aqi'],
        weather['water_availability_pct'],
        weather['power_availability_pct'],
        weather['humidity_pct']
    )

    locations = climate_service.get_all_locations()
    return render_template(
        'dashboard.html',
        location=location,
        weather=weather,
        aqi_data=aqi_data,
        risk=current_risk,
        locations=locations
    )

@dashboard_bp.route('/api/weather/<location>')
def get_weather_api(location):
    weather = climate_service.get_weather_by_location(location)
    aqi_data = aqi_service.get_aqi_by_location(location)
    if not weather:
        return jsonify({'error': 'Location not found'}), 404
    
    risk = risk_engine.compute_multi_factor_risk(
        weather['rainfall_mm'],
        weather['temperature_c'],
        aqi_data['aqi'],
        weather['water_availability_pct'],
        weather['power_availability_pct'],
        weather['humidity_pct']
    )
    return jsonify({
        'weather': weather,
        'aqi': aqi_data,
        'risk': risk
    })
