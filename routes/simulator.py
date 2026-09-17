from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from services.simulation_engine import SimulationEngine
from services.recommendation_engine import RecommendationEngine
from services.climate_service import ClimateService
from models.database import db
from models.models import Scenario, ScenarioResult
import json

simulator_bp = Blueprint('simulator', __name__)
simulation_engine = SimulationEngine()
recommendation_engine = RecommendationEngine()
climate_service = ClimateService()

@simulator_bp.route('/simulator')
def simulator():
    location = request.args.get('location', 'Pune')
    weather = climate_service.get_weather_by_location(location)
    presets = simulation_engine.get_presets()
    locations = climate_service.get_all_locations()
    return render_template(
        'simulator.html',
        location=location,
        weather=weather,
        presets=presets,
        locations=locations
    )

@simulator_bp.route('/results')
def results():
    # If rendering direct demo or query params
    location = request.args.get('location', 'Pune')
    rainfall = request.args.get('rainfall', default=150.0, type=float)
    temp = request.args.get('temperature', default=33.0, type=float)
    aqi = request.args.get('aqi', default=185, type=int)
    water = request.args.get('water', default=70.0, type=float)
    power = request.args.get('power', default=100.0, type=float)

    sim_result = simulation_engine.simulate(
        location=location,
        rainfall=rainfall,
        temp=temp,
        aqi=aqi,
        water_avail=water,
        power_avail=power
    )

    recommendations = recommendation_engine.generate_recommendations(sim_result)
    
    return render_template(
        'results.html',
        sim=sim_result,
        recommendations=recommendations,
        raw_json=json.dumps(sim_result)
    )

@simulator_bp.route('/api/simulate', methods=['POST'])
def api_simulate():
    data = request.get_json() or {}
    location = data.get('location', 'Pune')
    rainfall = float(data.get('rainfall', 150.0))
    temp = float(data.get('temperature', 33.0))
    aqi = int(data.get('aqi', 185))
    water = float(data.get('water_availability', data.get('water', 70.0)))
    power = float(data.get('power_availability', data.get('power', 100.0)))

    sim_result = simulation_engine.simulate(
        location=location,
        rainfall=rainfall,
        temp=temp,
        aqi=aqi,
        water_avail=water,
        power_avail=power
    )

    recs = recommendation_engine.generate_recommendations(sim_result)
    
    return jsonify({
        'simulation': sim_result,
        'recommendations': recs,
        'status': 'success'
    })

@simulator_bp.route('/api/scenarios/save', methods=['POST'])
def save_scenario():
    data = request.get_json() or {}
    name = data.get('name', 'Custom Scenario')
    location = data.get('location', 'Pune')
    description = data.get('description', 'Simulated via CLIMATEX What-If Engine')
    
    rainfall = float(data.get('rainfall', 150.0))
    temp = float(data.get('temperature', 33.0))
    aqi = int(data.get('aqi', 185))
    water = float(data.get('water_availability', 70.0))
    power = float(data.get('power_availability', 100.0))

    # Run simulation to store results snapshot
    sim_result = simulation_engine.simulate(
        location=location,
        rainfall=rainfall,
        temp=temp,
        aqi=aqi,
        water_avail=water,
        power_avail=power
    )
    sim_risk = sim_result['simulated']['risk']

    scenario = Scenario(
        name=name,
        location_name=location,
        description=description,
        rainfall_mm=rainfall,
        temperature_c=temp,
        aqi=aqi,
        water_availability_pct=water,
        power_availability_pct=power
    )
    db.session.add(scenario)
    db.session.flush()

    res = ScenarioResult(
        scenario_id=scenario.id,
        flood_risk=sim_risk['flood_risk'],
        heat_risk=sim_risk['heat_risk'],
        air_quality_risk=sim_risk['air_quality_risk'],
        water_risk=sim_risk['water_risk'],
        overall_risk=sim_risk['overall_risk'],
        exposure_score=sim_risk['exposure_score'],
        population_exposed=sim_result['simulated']['exposed_population'],
        roads_at_risk=sim_result['simulated']['roads_at_risk'],
        hospitals_exposed=sim_result['simulated']['hospitals_exposed'],
        details_json=json.dumps(sim_result)
    )
    db.session.add(res)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'scenario_id': scenario.id,
        'message': 'Scenario saved successfully to database.'
    })

@simulator_bp.route('/api/scenarios', methods=['GET'])
def get_all_scenarios():
    scenarios = Scenario.query.order_by(Scenario.created_at.desc()).all()
    out = []
    for sc in scenarios:
        s_dict = sc.to_dict()
        if sc.results:
            s_dict['result'] = sc.results[0].to_dict()
        out.append(s_dict)
    return jsonify({'scenarios': out})

@simulator_bp.route('/api/scenario/<int:scenario_id>', methods=['GET'])
def get_scenario_by_id(scenario_id):
    sc = db.session.get(Scenario, scenario_id)
    if not sc:
        return jsonify({'error': 'Scenario not found'}), 404
    s_dict = sc.to_dict()
    if sc.results:
        s_dict['result'] = sc.results[0].to_dict()
    return jsonify(s_dict)
