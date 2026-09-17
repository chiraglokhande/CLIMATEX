from flask import Flask, render_template
from config import Config
from models.database import db, init_db
from models.models import Location, User, Scenario, ScenarioResult
from routes import register_blueprints
from services.simulation_engine import SimulationEngine
import json

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Database
    init_db(app)

    # Register Blueprints
    register_blueprints(app)

    # Seed Database on Startup if needed
    with app.app_context():
        seed_database()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', not_found=True), 404

    return app

def seed_database():
    """Populate default reference locations and initial demo scenario if empty."""
    if Location.query.count() == 0:
        locations = [
            Location(name="Pune", state="Maharashtra", lat=18.5204, lon=73.8567, elevation_m=560.0, base_population=3950000),
            Location(name="Mumbai", state="Maharashtra", lat=19.0760, lon=72.8777, elevation_m=14.0, base_population=12500000),
            Location(name="Nashik", state="Maharashtra", lat=19.9975, lon=73.7898, elevation_m=584.0, base_population=1580000),
            Location(name="Nagpur", state="Maharashtra", lat=21.1458, lon=79.0882, elevation_m=310.0, base_population=2450000),
        ]
        db.session.bulk_save_objects(locations)
        db.session.commit()

    # Pre-seed Ready-to-Run Demo Scenario: Pune Heavy Rainfall (+50%)
    if Scenario.query.count() == 0:
        sim_engine = SimulationEngine()
        demo_sim = sim_engine.simulate(
            location="Pune",
            rainfall=150.0,
            temp=33.0,
            aqi=185,
            water_avail=70.0,
            power_avail=100.0
        )
        sim_risk = demo_sim['simulated']['risk']

        demo_scenario = Scenario(
            name="Pune Heavy Monsoon Surge (+50% Rainfall)",
            location_name="Pune",
            description="Official Benchmark Demo: Heavy rainfall surge causing riverbank inundation and localized AQI particulate trap.",
            rainfall_mm=150.0,
            temperature_c=33.0,
            aqi=185,
            water_availability_pct=70.0,
            power_availability_pct=100.0
        )
        db.session.add(demo_scenario)
        db.session.flush()

        demo_result = ScenarioResult(
            scenario_id=demo_scenario.id,
            flood_risk=sim_risk['flood_risk'],
            heat_risk=sim_risk['heat_risk'],
            air_quality_risk=sim_risk['air_quality_risk'],
            water_risk=sim_risk['water_risk'],
            overall_risk=sim_risk['overall_risk'],
            exposure_score=sim_risk['exposure_score'],
            population_exposed=demo_sim['simulated']['exposed_population'],
            roads_at_risk=demo_sim['simulated']['roads_at_risk'],
            hospitals_exposed=demo_sim['simulated']['hospitals_exposed'],
            details_json=json.dumps(demo_sim)
        )
        db.session.add(demo_result)
        db.session.commit()

app = create_app()

import os
import socket

def get_port():
    if 'PORT' in os.environ:
        return int(os.environ['PORT'])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', 5000)) != 0:
            return 5000
    return 5001

if __name__ == '__main__':
    port = get_port()
    print("==================================================")
    print(" CLIMATEX - Environmental Decision Support System ")
    print(f" Running at: http://127.0.0.1:{port}             ")
    print("==================================================")
    app.run(host='127.0.0.1', port=port, debug=True)
