from flask import Blueprint, render_template, jsonify, request
from services.aqi_service import AQIService
from services.recommendation_engine import RecommendationEngine

aqi_bp = Blueprint('aqi', __name__)
aqi_service = AQIService()
recommendation_engine = RecommendationEngine()

@aqi_bp.route('/aqi')
def aqi_monitoring():
    location = request.args.get('location', 'Pune')
    aqi_data = aqi_service.get_aqi_by_location(location)
    causes_data = aqi_service.analyze_causes(location)
    return render_template('aqi.html', location=location, aqi_data=aqi_data, causes_data=causes_data)

@aqi_bp.route('/aqi-solutions')
def aqi_solutions():
    location = request.args.get('location', 'Pune')
    simulated_aqi = request.args.get('aqi', type=int)
    
    aqi_data = aqi_service.get_aqi_by_location(location)
    if simulated_aqi is not None:
        aqi_data['aqi'] = simulated_aqi
        cat, txt, bdg, clr = aqi_service.get_aqi_category(simulated_aqi)
        aqi_data['category'] = cat
        aqi_data['badge_class'] = bdg
        aqi_data['color_hex'] = clr

    causes_data = aqi_service.analyze_causes(location, simulated_aqi=simulated_aqi)
    
    return render_template(
        'aqi_solutions.html',
        location=location,
        aqi_data=aqi_data,
        causes_data=causes_data
    )

@aqi_bp.route('/api/aqi/<location>')
def get_aqi_api(location):
    aqi_data = aqi_service.get_aqi_by_location(location)
    if not aqi_data:
        return jsonify({'error': 'Location not found'}), 404
    causes = aqi_service.analyze_causes(location)
    return jsonify({
        'aqi_data': aqi_data,
        'causes': causes
    })
