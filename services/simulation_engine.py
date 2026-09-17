import json
import os
from .risk_engine import RiskEngine
from .climate_service import ClimateService
from .aqi_service import AQIService

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class SimulationEngine:
    def __init__(self):
        self.risk_engine = RiskEngine()
        self.climate_service = ClimateService()
        self.aqi_service = AQIService()
        self.roads_data = self._load_json('roads.json')
        self.hospitals_data = self._load_json('hospitals.json')
        self.population_data = self._load_json('population.json')

    def _load_json(self, filename):
        filepath = os.path.join(BASE_DIR, 'data', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_presets(self):
        return [
            {
                "id": "normal",
                "name": "Normal Conditions",
                "desc": "Baseline seasonal conditions with stable weather and normal traffic.",
                "rainfall": 60, "temp": 28, "aqi": 80, "water": 90, "power": 100
            },
            {
                "id": "heavy_rain",
                "name": "Heavy Rainfall (+50%)",
                "desc": "Intense localized monsoon cloudburst testing urban stormwater drainage.",
                "rainfall": 150, "temp": 27, "aqi": 65, "water": 95, "power": 85
            },
            {
                "id": "extreme_rain",
                "name": "Extreme Deluge / Cloudburst",
                "desc": "Severe rainfall exceeding 220mm, high river discharge and flash flood risks.",
                "rainfall": 240, "temp": 25, "aqi": 50, "water": 100, "power": 40
            },
            {
                "id": "heatwave",
                "name": "Severe Heatwave (Loo)",
                "desc": "Prolonged high ambient temperature with dry winds, straining water and grid cooling.",
                "rainfall": 0, "temp": 44, "aqi": 195, "water": 35, "power": 65
            },
            {
                "id": "high_aqi",
                "name": "High AQI / Smog Episode",
                "desc": "Atmospheric temperature inversion trapping particulate and industrial emissions.",
                "rainfall": 10, "temp": 31, "aqi": 285, "water": 75, "power": 95
            },
            {
                "id": "water_shortage",
                "name": "Severe Drought & Water Scarcity",
                "desc": "Depleted reservoir capacity, low municipal water supply during dry spell.",
                "rainfall": 5, "temp": 39, "aqi": 160, "water": 18, "power": 75
            },
            {
                "id": "compound_disaster",
                "name": "Power Outage + Heavy Rainfall",
                "desc": "Storm water flooding coinciding with grid tripping and automated pump failure.",
                "rainfall": 175, "temp": 26, "aqi": 70, "water": 85, "power": 20
            }
        ]

    def simulate(self, location="Pune", rainfall=150.0, temp=33.0, aqi=185, water_avail=70.0, power_avail=100.0):
        # 1. Baseline Data
        base_weather = self.climate_service.get_weather_by_location(location)
        base_aqi_obj = self.aqi_service.get_aqi_by_location(location)

        base_rainfall = base_weather.get('rainfall_mm', 100.0)
        base_temp = base_weather.get('temperature_c', 30.0)
        base_aqi = base_aqi_obj.get('aqi', 120) if base_aqi_obj else 120
        base_water = base_weather.get('water_availability_pct', 80.0)
        base_power = base_weather.get('power_availability_pct', 100.0)

        # 2. Risk Evaluation (Current vs Simulated)
        current_risk = self.risk_engine.compute_multi_factor_risk(
            base_rainfall, base_temp, base_aqi, base_water, base_power
        )
        simulated_risk = self.risk_engine.compute_multi_factor_risk(
            rainfall, temp, aqi, water_avail, power_avail
        )

        # 3. Road Accessibility Evaluation
        city_roads = self.roads_data.get(location, self.roads_data.get('Pune', []))
        simulated_roads = []
        roads_at_risk_count = 0
        base_roads_at_risk_count = 0

        for rd in city_roads:
            thresh = rd.get('flood_threshold_mm', 130.0)
            
            # Baseline road status
            if base_rainfall >= thresh:
                base_status = "Potentially Inaccessible"
                base_roads_at_risk_count += 1
            elif base_rainfall >= (thresh * 0.75):
                base_status = "Disruption Risk"
                base_roads_at_risk_count += 1
            else:
                base_status = "Safe"

            # Simulated road status
            if rainfall >= thresh:
                status = "Potentially Inaccessible"
                status_class = "badge-danger"
                color = "#EF4444"
                roads_at_risk_count += 1
            elif rainfall >= (thresh * 0.75):
                status = "High Disruption Risk"
                status_class = "badge-warning"
                color = "#F59E0B"
                roads_at_risk_count += 1
            else:
                status = "Safe / Clear"
                status_class = "badge-success"
                color = "#10B981"

            simulated_roads.append({
                'id': rd.get('id'),
                'name': rd.get('name'),
                'coordinates': rd.get('coordinates'),
                'elevation_m': rd.get('elevation_m'),
                'flood_threshold_mm': thresh,
                'status': status,
                'status_class': status_class,
                'color': color,
                'is_emergency_route': rd.get('is_emergency_route', False),
                'alt_route': rd.get('alt_route', 'Alternative Corridor Available')
            })

        # 4. Critical Infrastructure Evaluation
        city_inf = self.hospitals_data.get(location, self.hospitals_data.get('Pune', []))
        simulated_infrastructure = []
        hospitals_exposed_count = 0
        base_hospitals_exposed_count = 0
        safe_shelters_count = 0

        for inf in city_inf:
            itype = inf.get('type')
            vuln = inf.get('flood_vulnerability', 'Medium')
            
            # Vulnerability threshold based on elevation & structure
            vuln_factor = 1.0 if vuln == 'High' else (1.4 if vuln == 'Medium' else 1.8)
            effective_thresh = 110.0 * vuln_factor

            # Heatwave or power outage vulnerability
            power_affected = (power_avail < 50 and itype in ['Hospital', 'Water Facility'])
            heat_stressed = (temp > 40 and itype == 'Hospital')

            is_at_risk = (rainfall >= effective_thresh) or power_affected or (temp > 42 and vuln == 'High')
            
            if base_rainfall >= effective_thresh:
                if itype == 'Hospital':
                    base_hospitals_exposed_count += 1

            if is_at_risk:
                if itype == 'Hospital':
                    hospitals_exposed_count += 1
                    status_note = "Potentially Exposed / High Surge Protocol"
                    status_badge = "badge-danger"
                elif itype == 'Shelter':
                    status_note = "Site Flood Risk / Relocation Advised"
                    status_badge = "badge-warning"
                else:
                    status_note = "Grid Strain / Facility Monitored"
                    status_badge = "badge-danger"
            else:
                if itype == 'Shelter':
                    safe_shelters_count += 1
                    status_note = "Safe Haven Operational"
                    status_badge = "badge-success"
                else:
                    status_note = "Operational & Secure"
                    status_badge = "badge-success"

            simulated_infrastructure.append({
                'id': inf.get('id'),
                'name': inf.get('name'),
                'type': itype,
                'lat': inf.get('lat'),
                'lon': inf.get('lon'),
                'capacity': inf.get('capacity'),
                'status_note': status_note,
                'status_badge': status_badge,
                'is_at_risk': is_at_risk,
                'criticality': inf.get('criticality', 'High')
            })

        # 5. Population Exposure Modelling
        pop_city_data = self.population_data.get(location, self.population_data.get('Pune', {}))
        total_pop = pop_city_data.get('total_population', 3500000)
        wards = pop_city_data.get('wards', [])

        # Exposure multiplier based on rainfall, temp, and AQI
        flood_mult = min(1.0, max(0.0, (rainfall - 40) / 200.0))
        aqi_mult = min(1.0, max(0.0, (aqi - 80) / 350.0))
        heat_mult = min(1.0, max(0.0, (temp - 30) / 20.0))

        base_flood_mult = min(1.0, max(0.0, (base_rainfall - 40) / 200.0))

        # Modelled Exposed Population
        simulated_exposed_pop = int(total_pop * (0.45 * flood_mult + 0.35 * aqi_mult + 0.20 * heat_mult))
        base_exposed_pop = int(total_pop * (0.45 * base_flood_mult + 0.35 * min(1.0, max(0.0, (base_aqi - 80)/350.0))))

        high_risk_pop = int(simulated_exposed_pop * 0.45)
        med_risk_pop = int(simulated_exposed_pop * 0.38)
        low_risk_pop = max(0, total_pop - high_risk_pop - med_risk_pop)

        # Polygon risk zones for map
        risk_zones = []
        for ward in wards:
            w_fs = ward.get('flood_susceptibility', 'Medium')
            
            # Elevate ward risk under simulation
            if rainfall > 140 and w_fs in ['High', 'Critical']:
                zone_risk = 'CRITICAL'
                zone_color = '#7C3AED'
                fill_color = '#7C3AED'
                opacity = 0.5
            elif rainfall > 100 or aqi > 200 or temp > 38:
                zone_risk = 'HIGH' if w_fs in ['High', 'Critical'] else 'MEDIUM'
                zone_color = '#EF4444' if zone_risk == 'HIGH' else '#F59E0B'
                fill_color = '#EF4444' if zone_risk == 'HIGH' else '#F59E0B'
                opacity = 0.4
            else:
                zone_risk = 'LOW'
                zone_color = '#10B981'
                fill_color = '#10B981'
                opacity = 0.25

            risk_zones.append({
                'name': ward.get('name'),
                'population': ward.get('population'),
                'density_per_sqkm': ward.get('density_per_sqkm'),
                'zone_risk': zone_risk,
                'color': zone_color,
                'fill_color': fill_color,
                'opacity': opacity,
                'polygon': ward.get('polygon')
            })

        return {
            'location': location,
            'is_modelled_simulation': True,
            'inputs': {
                'rainfall_mm': rainfall,
                'temperature_c': temp,
                'aqi': aqi,
                'water_availability_pct': water_avail,
                'power_availability_pct': power_avail
            },
            'baseline': {
                'rainfall_mm': base_rainfall,
                'temperature_c': base_temp,
                'aqi': base_aqi,
                'water_availability_pct': base_water,
                'power_availability_pct': base_power,
                'risk': current_risk,
                'roads_at_risk': base_roads_at_risk_count,
                'hospitals_exposed': base_hospitals_exposed_count,
                'exposed_population': base_exposed_pop
            },
            'simulated': {
                'risk': simulated_risk,
                'roads_at_risk': roads_at_risk_count,
                'hospitals_exposed': hospitals_exposed_count,
                'safe_shelters': safe_shelters_count,
                'exposed_population': simulated_exposed_pop,
                'population_breakdown': {
                    'total': total_pop,
                    'high_risk': high_risk_pop,
                    'medium_risk': med_risk_pop,
                    'low_risk': low_risk_pop
                }
            },
            'roads': simulated_roads,
            'infrastructure': simulated_infrastructure,
            'risk_zones': risk_zones
        }
