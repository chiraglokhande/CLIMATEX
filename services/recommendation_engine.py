class RecommendationEngine:
    """
    Intelligent Environmental Decision-Support & Action Recommendation Engine.
    Generates actionable, categorized municipal & emergency recommendations based on simulated scenarios.
    Clearly marked as decision-support guidelines.
    """

    def generate_recommendations(self, sim_data):
        inputs = sim_data.get('inputs', {})
        simulated = sim_data.get('simulated', {})
        risk = simulated.get('risk', {})
        
        rainfall = inputs.get('rainfall_mm', 100)
        temp = inputs.get('temperature_c', 30)
        aqi = inputs.get('aqi', 100)
        water = inputs.get('water_availability_pct', 80)
        power = inputs.get('power_availability_pct', 100)

        overall_risk = risk.get('overall_risk', 'MEDIUM')
        flood_risk = risk.get('flood_risk', 'LOW')
        heat_risk = risk.get('heat_risk', 'LOW')
        aqi_risk = risk.get('air_quality_risk', 'LOW')
        water_risk = risk.get('water_risk', 'LOW')
        power_risk = risk.get('power_risk', 'LOW')

        actions = {
            'immediate': [],
            'operational': [],
            'infrastructure': [],
            'public_advisory': []
        }

        # --- FLOOD & HEAVY RAIN RECOMMENDATIONS ---
        if flood_risk in ['HIGH', 'CRITICAL'] or rainfall >= 140:
            actions['immediate'].append({
                'title': 'Deploy Emergency Quick-Response Flood Teams (NDRF / SDRF)',
                'desc': 'Pre-position inflatable rescue boats and dewatering pump sets near low-lying riverbank sectors and known choke points.',
                'domain': 'Emergency Response',
                'priority': 'Urgent',
                'badge': 'bg-danger'
            })
            actions['immediate'].append({
                'title': 'Initiate Road Traffic Diversions for Low-Lying Corridors',
                'desc': 'Reroute commuter and freight traffic away from low causeways and subways towards elevated bypass arteries.',
                'domain': 'Mobility & Traffic',
                'priority': 'Urgent',
                'badge': 'bg-danger'
            })
            actions['operational'].append({
                'title': 'Activate Designated High-Ground Emergency Shelters',
                'desc': 'Equip identified community relief halls with dry rations, emergency medical kits, clean drinking water, and backup gensets.',
                'domain': 'Shelter Management',
                'priority': 'High',
                'badge': 'bg-warning text-dark'
            })
            actions['public_advisory'].append({
                'title': 'Issue Localized Flash-Flood & Inundation Warning',
                'desc': 'Advise citizens in river basin wards to avoid non-essential transit and secure ground-floor electrical appliances.',
                'domain': 'Public Warning',
                'priority': 'Urgent',
                'badge': 'bg-danger'
            })
        elif flood_risk == 'MEDIUM':
            actions['operational'].append({
                'title': 'Inspect Stormwater Inlets & Pumping Stations',
                'desc': 'Clear debris from primary drainage culverts and ensure emergency diesel generators at pump houses are fueled.',
                'domain': 'Municipal Engineering',
                'priority': 'Medium',
                'badge': 'bg-info text-dark'
            })

        # --- AIR QUALITY & AQI MITIGATION ---
        if aqi_risk in ['HIGH', 'CRITICAL'] or aqi >= 180:
            actions['immediate'].append({
                'title': 'Deploy Anti-Smog Guns & Mechanical Road Water Sprinklers',
                'desc': 'Mobilize misting vehicles across top particulate hotspots and heavy traffic junctions to suppress resuspended road dust.',
                'domain': 'Pollution Abatement',
                'priority': 'Urgent',
                'badge': 'bg-danger'
            })
            actions['operational'].append({
                'title': 'Enforce Construction Dust Control & Material Covering',
                'desc': 'Mandate water sprinkling at all active construction sites; halt open aggregate loading and non-compliant demolition works.',
                'domain': 'Enforcement',
                'priority': 'High',
                'badge': 'bg-warning text-dark'
            })
            actions['operational'].append({
                'title': 'Heavy Diesel Freight Restriction in Core Urban Zones',
                'desc': 'Temporarily restrict non-essential heavy commercial vehicles from entering inner ring corridors during peak inversion hours.',
                'domain': 'Traffic Management',
                'priority': 'High',
                'badge': 'bg-warning text-dark'
            })
            actions['public_advisory'].append({
                'title': 'Issue High Pollution Health Advisory',
                'desc': 'Advise vulnerable groups (elderly, children, respiratory patients) to minimize strenuous outdoor physical activities and use N95 masks.',
                'domain': 'Public Health',
                'priority': 'High',
                'badge': 'bg-warning text-dark'
            })
        elif aqi_risk == 'MEDIUM':
            actions['operational'].append({
                'title': 'Intensify Surveillance on Open Waste Burning',
                'desc': 'Deploy municipal flying squads to monitor and penalize open garbage or dry leaf incineration in peripheral wards.',
                'domain': 'Environmental Compliance',
                'priority': 'Medium',
                'badge': 'bg-info text-dark'
            })

        # --- HEATWAVE MITIGATION ---
        if heat_risk in ['HIGH', 'CRITICAL'] or temp >= 40:
            actions['immediate'].append({
                'title': 'Establish Public Cooling Centers & ORS Hydration Booths',
                'desc': 'Open air-cooled municipal community centers and set up oral rehydration solution distribution kiosks at major bus terminals.',
                'domain': 'Public Health',
                'priority': 'Urgent',
                'badge': 'bg-danger'
            })
            actions['operational'].append({
                'title': 'Adjust Outdoor Labor Timings (Noon Respite)',
                'desc': 'Enforce mandatory rest breaks between 12:00 PM and 3:30 PM for outdoor construction workers and street vendors.',
                'domain': 'Labor Welfare',
                'priority': 'High',
                'badge': 'bg-warning text-dark'
            })
            actions['public_advisory'].append({
                'title': 'Heat Stress & Hydration Public Warning',
                'desc': 'Broadcast advisory on symptoms of heat stroke and encourage frequent water intake and light clothing.',
                'domain': 'Public Health',
                'priority': 'High',
                'badge': 'bg-warning text-dark'
            })

        # --- WATER SCARCITY MITIGATION ---
        if water_risk in ['HIGH', 'CRITICAL'] or water <= 40:
            actions['infrastructure'].append({
                'title': 'Ration Municipal Water & Mobilize Emergency Tanker Fleets',
                'desc': 'Schedule equitable rotational supply and deploy GPS-tracked municipal water tankers to water-deficit wards.',
                'domain': 'Water Supply',
                'priority': 'High',
                'badge': 'bg-warning text-dark'
            })
            actions['infrastructure'].append({
                'title': 'Restrict Non-Potable Commercial Water Consumption',
                'desc': 'Prohibit potable water usage for vehicle washing, decorative fountains, and commercial gardening.',
                'domain': 'Conservation',
                'priority': 'High',
                'badge': 'bg-warning text-dark'
            })

        # --- POWER & GRID STABILITY ---
        if power_risk in ['HIGH', 'CRITICAL'] or power <= 50:
            actions['infrastructure'].append({
                'title': 'Prioritize Hospital & Critical Infrastructure Auxiliary Power',
                'desc': 'Verify fuel reserves for secondary generator sets at all public hospitals, water treatment plants, and emergency communications centers.',
                'domain': 'Energy & Utilities',
                'priority': 'Urgent',
                'badge': 'bg-danger'
            })
            actions['infrastructure'].append({
                'title': 'Deploy Mobile Emergency Generator Sets',
                'desc': 'Position rapid-deployment mobile transformers and gensets near flood-drainage pump stations to avert waterlogging.',
                'domain': 'Grid Operations',
                'priority': 'High',
                'badge': 'bg-warning text-dark'
            })

        # Fallback if all conditions normal
        if not actions['immediate'] and not actions['operational']:
            actions['operational'].append({
                'title': 'Maintain Standard Environmental Surveillance',
                'desc': 'Continue scheduled sensor telemetry checks, routine road maintenance, and regular air monitoring.',
                'domain': 'Routine Monitoring',
                'priority': 'Normal',
                'badge': 'bg-success'
            })

        return {
            'overall_risk': overall_risk,
            'summary': f"Identified {len(actions['immediate'])} immediate response directives and {len(actions['operational'])} operational mitigation measures based on modelled conditions.",
            'actions': actions
        }
