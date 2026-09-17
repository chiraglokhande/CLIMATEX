from .main import main_bp
from .dashboard import dashboard_bp
from .aqi import aqi_bp
from .simulator import simulator_bp
from .map_routes import map_bp
from .reports import reports_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(aqi_bp)
    app.register_blueprint(simulator_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(reports_bp)
