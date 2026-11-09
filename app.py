from flask import Flask, render_template, session, send_from_directory, request, redirect, url_for, jsonify, flash
from config import Config
from models.database import db, init_db
from models.models import Location, User, Scenario, ScenarioResult
from routes import register_blueprints
from services.simulation_engine import SimulationEngine
import json
import os
import socket

def create_app(config_class=Config):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_folder = os.path.join(base_dir, 'static')
    if not os.path.exists(static_folder):
        static_folder = os.path.join(base_dir, 'public', 'static')

    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    app.config.from_object(config_class)

    # Initialize Database
    init_db(app)

    # Register Blueprints
    register_blueprints(app)

    # Strict Feature Access Control: All features require authentication
    @app.before_request
    def enforce_feature_login():
        public_endpoints = {
            'main.index',
            'auth.login',
            'auth.register',
            'auth.demo_login',
            'auth.logout',
            'serve_css',
            'static'
        }

        endpoint = request.endpoint
        if endpoint and (endpoint in public_endpoints or endpoint.startswith('static')):
            return None

        # Allow static files and asset requests
        path = request.path
        if (
            path.startswith('/static/') or
            path.startswith('/css/') or
            path == '/favicon.ico' or
            path in ('/', '/login', '/register', '/demo-login', '/logout')
        ):
            return None

        # If user is not logged in, block access to any feature!
        if not session.get('user_id'):
            if path.startswith('/api/'):
                return jsonify({
                    'status': 'error',
                    'message': 'Unauthorized: Access restricted. Please sign in or register to use CLIMATEX features.',
                    'redirect': url_for('auth.login')
                }), 401

            flash('Please sign in or create an account to access CLIMATEX platform features.', 'warning')
            target = request.full_path if request.query_string else request.path
            return redirect(url_for('auth.login', next=target))

    # Anti-Caching & Per-Device Session Isolation: Prevent edge proxies / CDNs from caching rendered user HTML
    @app.after_request
    def set_cache_control_headers(response):
        path = request.path
        if not path.startswith('/static/') and not path.startswith('/css/') and path != '/favicon.ico':
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Vary'] = 'Cookie, Accept-Encoding'
        return response

    # Global Context Processor for Authentication
    @app.context_processor
    def inject_auth_globals():
        current_user = None
        user_id = session.get('user_id')
        if user_id:
            try:
                current_user = db.session.get(User, user_id)
            except Exception:
                current_user = None
        return {
            'current_user': current_user,
            'is_authenticated': current_user is not None
        }

    # Seed Database on Startup if needed
    with app.app_context():
        seed_database()

    # Explicit route for /css/
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        for candidate in [
            os.path.join(base_dir, 'public', 'css'),
            os.path.join(base_dir, 'static', 'css')
        ]:
            if os.path.exists(os.path.join(candidate, filename)):
                return send_from_directory(candidate, filename, mimetype='text/css')
        return "Not found", 404

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

def seed_database():
    """Populate default reference locations, demo analyst user, and initial demo scenario if empty."""
    try:
        # Seed Default Analyst User for instant demo/testing
        if User.query.count() == 0:
            demo_user = User(
                username="analyst_demo",
                email="analyst@climatex.org",
                full_name="Dr. Aisha Roy",
                role="Senior Environmental Analyst"
            )
            demo_user.set_password("Climatex2026!")
            db.session.add(demo_user)
            db.session.commit()
            print("[Database] Seeded demo analyst user: analyst_demo / Climatex2026!")

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
    except Exception as e:
        print(f"[Database] Warning during seeding: {e}")
        try:
            db.session.rollback()
        except Exception:
            pass

app = create_app()

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
