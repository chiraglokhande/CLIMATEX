from flask import Blueprint, render_template, jsonify, request, send_file, redirect, url_for
from models.database import db
from models.models import Scenario, ScenarioResult
from services.recommendation_engine import RecommendationEngine
from services.simulation_engine import SimulationEngine
import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

reports_bp = Blueprint('reports', __name__)
recommendation_engine = RecommendationEngine()
simulation_engine = SimulationEngine()

@reports_bp.route('/reports')
def reports_page():
    scenarios = Scenario.query.order_by(Scenario.created_at.desc()).all()
    return render_template('reports.html', scenarios=scenarios)

@reports_bp.route('/api/recommendations', methods=['POST'])
def api_recommendations():
    data = request.get_json() or {}
    location = data.get('location', 'Pune')
    rainfall = float(data.get('rainfall', 150.0))
    temp = float(data.get('temperature', 33.0))
    aqi = int(data.get('aqi', 185))
    water = float(data.get('water_availability', 70.0))
    power = float(data.get('power_availability', 100.0))

    sim_result = simulation_engine.simulate(location, rainfall, temp, aqi, water, power)
    recs = recommendation_engine.generate_recommendations(sim_result)
    return jsonify(recs)

@reports_bp.route('/reports/download/<int:scenario_id>')
def download_pdf(scenario_id):
    scenario = db.session.get(Scenario, scenario_id)
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404
    result = scenario.results[0] if scenario.results else None
    
    details = json.loads(result.details_json) if result and result.details_json else {}

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0284C7'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )
    disclaimer_style = ParagraphStyle(
        'DocDisclaimer',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#DC2626')
    )

    story = []

    # Title & Header
    story.append(Paragraph("CLIMATEX – AI Climate Risk & Decision Support Report", title_style))
    story.append(Paragraph(f"Generated for Scenario: <b>{scenario.name}</b> | Location: <b>{scenario.location_name}</b> | Date: {scenario.created_at.strftime('%B %d, %Y %H:%M')}", subtitle_style))
    story.append(Paragraph("<b>IMPORTANT NOTICE:</b> All values and impacts in this report represent MODELLED / ESTIMATED results for decision support and emergency preparedness planning, not guaranteed real-world forecasts.", disclaimer_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceAfter=12))

    # Input Parameters Table
    story.append(Paragraph("1. Simulated Input Parameters", section_heading))
    input_data = [
        ['Parameter', 'Simulated Value', 'Baseline Value', 'Unit'],
        ['Rainfall', f"{scenario.rainfall_mm} mm", f"{details.get('baseline', {}).get('rainfall_mm', 100)} mm", "Millimeters (24h)"],
        ['Ambient Temperature', f"{scenario.temperature_c} °C", f"{details.get('baseline', {}).get('temperature_c', 30)} °C", "Degrees Celsius"],
        ['Air Quality Index (AQI)', f"{scenario.aqi}", f"{details.get('baseline', {}).get('aqi', 120)}", "AQI Index"],
        ['Water Availability', f"{scenario.water_availability_pct} %", f"{details.get('baseline', {}).get('water_availability_pct', 80)} %", "Percentage"],
        ['Grid Power Availability', f"{scenario.power_availability_pct} %", f"{details.get('baseline', {}).get('power_availability_pct', 100)} %", "Percentage"]
    ]
    t_inputs = Table(input_data, colWidths=[150, 120, 120, 140])
    t_inputs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white])
    ]))
    story.append(t_inputs)
    story.append(Spacer(1, 12))

    # Risk Assessment Results Table
    if result:
        story.append(Paragraph("2. Multi-Factor Risk Assessment", section_heading))
        risk_data = [
            ['Risk Dimension', 'Evaluated Level', 'Baseline Level', 'Status'],
            ['Overall Environmental Risk', result.overall_risk, details.get('baseline', {}).get('risk', {}).get('overall_risk', 'MED'), f"Score: {result.exposure_score}/100"],
            ['Flood Risk', result.flood_risk, details.get('baseline', {}).get('risk', {}).get('flood_risk', 'LOW'), 'Inundation Potential'],
            ['Heat Risk', result.heat_risk, details.get('baseline', {}).get('risk', {}).get('heat_risk', 'LOW'), 'Thermal Stress Index'],
            ['Air Quality Risk', result.air_quality_risk, details.get('baseline', {}).get('risk', {}).get('air_quality_risk', 'MED'), 'Exposure Risk'],
            ['Water Risk', result.water_risk, details.get('baseline', {}).get('risk', {}).get('water_risk', 'LOW'), 'Municipal Deficit']
        ]
        t_risk = Table(risk_data, colWidths=[160, 110, 110, 150])
        t_risk.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284C7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white])
        ]))
        story.append(t_risk)
        story.append(Spacer(1, 12))

    # Impact Summary Table
    story.append(Paragraph("3. Modelled Infrastructure & Population Impact", section_heading))
    impact_data = [
        ['Impact Dimension', 'Modelled Simulated Value', 'Baseline Condition'],
        ['Potentially Exposed Population', f"{result.population_exposed:,} citizens", f"{details.get('baseline', {}).get('exposed_population', 0):,} citizens"],
        ['Road Corridors at Disruption Risk', f"{result.roads_at_risk} corridors", f"{details.get('baseline', {}).get('roads_at_risk', 0)} corridors"],
        ['Hospitals Potentially Exposed/Strained', f"{result.hospitals_exposed} facilities", f"{details.get('baseline', {}).get('hospitals_exposed', 0)} facilities"],
        ['Safe Haven Shelters Operational', f"{details.get('simulated', {}).get('safe_shelters', 0)} shelters", "Standard Standby"]
    ]
    t_impact = Table(impact_data, colWidths=[200, 160, 170])
    t_impact.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#047857')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white])
    ]))
    story.append(t_impact)
    story.append(Spacer(1, 12))

    # Recommendations Section
    story.append(Paragraph("4. Recommended Decision-Support Directives", section_heading))
    if details:
        recs = recommendation_engine.generate_recommendations(details)
        for cat, act_list in recs.get('actions', {}).items():
            if act_list:
                cat_title = cat.replace('_', ' ').capitalize()
                story.append(Paragraph(f"<b>[{cat_title}]</b>", ParagraphStyle('Sub', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A'))))
                for a in act_list:
                    story.append(Paragraph(f"• <b>{a['title']}</b>: {a['desc']}", body_style))
                story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"CLIMATEX_Scenario_{scenario.location_name}_{scenario.id}.pdf",
        mimetype='application/pdf'
    )

@reports_bp.route('/api/scenarios/delete/<int:scenario_id>', methods=['POST'])
def delete_scenario(scenario_id):
    sc = db.session.get(Scenario, scenario_id)
    if not sc:
        return jsonify({'error': 'Scenario not found'}), 404
    db.session.delete(sc)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Scenario deleted successfully'})
