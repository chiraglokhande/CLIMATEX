# CLIMATEX – AI-Powered Climate Risk & Environmental Decision Support System

[![Flask](https://img.shields.io/badge/Flask-3.1-blue.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.12-green.svg)](https://www.python.org/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-brightgreen.svg)](https://leafletjs.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-orange.svg)](https://www.chartjs.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)

**CLIMATEX** is a complete, modern, working AI-assisted climate risk and environmental decision-support platform designed for urban municipal resilience, emergency disaster management, and environmental policy planning.

---

## 🌟 Key Modules

### 1. 🍃 Module 1: AQI Monitoring & Solution Engine
- **Real-Time Telemetry & Monitoring:** Comprehensive tracking of criteria air pollutants (`PM2.5`, `PM10`, `NO2`, `SO2`, `CO`, `O3`) across urban sectors.
- **Root-Cause Diagnostic Engine:** Solves the core question: *"Why is AQI high?"* by estimating source contributions (vehicular traffic, construction dust, industrial emissions, and open biomass burning).
- **Categorized Mitigation Actions:** Provides actionable, prioritized municipal decision-support directives (dust suppression, transit phasing, flying squad patrols, stack controls).

### 2. ⚡ Module 2: What-If Climate Simulator (Main Centerpiece)
- **Interactive Multi-Parameter Sliders:**
  - 🌧️ Rainfall: `0 – 300 mm` (Baseline: 100 mm)
  - 🌡️ Temperature: `15 – 50 °C` (Baseline: 30 °C)
  - 💨 Air Quality Index: `0 – 500 AQI` (Baseline: 120)
  - 💧 Water Availability: `0 – 100 %` (Baseline: 80%)
  - ⚡ Power Grid Availability: `0 – 100 %` (Baseline: 100%)
- **Pre-Configured Scenario Presets:**
  1. *Normal Conditions*
  2. *Heavy Rainfall (+50% Surge)*
  3. *Extreme Deluge / Cloudburst*
  4. *Severe Heatwave (Loo)*
  5. *High AQI / Smog Episode*
  6. *Severe Drought & Water Scarcity*
  7. *Compound Disaster (Power Outage + Heavy Rain)*
  8. *Custom Scenario*
- **Modelled Multi-Hazard Impact Projections:**
  - **Road Accessibility:** Identifies corridors at risk of waterlogging / disruption and suggests alternative emergency routes.
  - **Critical Infrastructure:** Tracks vulnerability of hospitals, relief shelters, water plants, and grid substations.
  - **Population Exposure:** Models total and ward-level vulnerable citizen counts.
  - **Before vs. After Comparative Dashboard:** Side-by-side metric delta comparison.
  - **Official PDF Report Generation:** Instantly downloads formal PDF briefings using ReportLab.

### 3. 🗺️ Module 3: Interactive GIS Risk Map
- Multi-layer Leaflet.js map with color-coded flood risk polygons (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), road accessibility corridors, hospital surge markers, safe shelters, and AQI pollution hotspots.

---

## 🏗️ Architecture Overview

```text
climatex/
│
├── app.py                      # Flask Application Factory & Seed Runner
├── config.py                   # Configuration Settings & Database URI
├── requirements.txt            # Python Dependencies
├── README.md                   # System Documentation
│
├── models/                     # SQLAlchemy Data Layer
│   ├── __init__.py
│   ├── database.py             # DB instance & init_db()
│   └── models.py               # User, Location, AQI, Weather, Road, Scenario
│
├── routes/                     # Flask Blueprint Route Handlers
│   ├── __init__.py
│   ├── main.py                 # Landing page & About routes
│   ├── dashboard.py            # Dashboard & Weather telemetry APIs
│   ├── aqi.py                  # AQI Monitoring & Solution Engine
│   ├── simulator.py            # What-If Simulator & Results
│   ├── map_routes.py           # GIS Map & Map Data APIs
│   └── reports.py              # Scenario Archive & PDF Generator
│
├── services/                   # Business Logic & AI Engines
│   ├── __init__.py
│   ├── aqi_service.py          # AQI calculation & source attribution
│   ├── climate_service.py      # Weather telemetry & location profiles
│   ├── risk_engine.py          # Multi-factor explainable risk scoring
│   ├── simulation_engine.py    # Spatial & topological impact modeling
│   └── recommendation_engine.py# Context-aware mitigation generator
│
├── data/                       # Structured Sample & GIS Datasets
│   ├── aqi_sample.json         # Ward-level pollutants & historical trends
│   ├── weather_sample.json     # Climate baselines & temperature curves
│   ├── roads.json              # Road network coordinates & flood thresholds
│   ├── hospitals.json          # Hospitals, shelters & critical assets
│   └── population.json         # Ward polygons & demographic densities
│
├── templates/                  # Modern Jinja2 HTML5 Templates
│   ├── base.html               # Global layout, navbar & footer
│   ├── index.html              # Modern Climate-Tech Landing Page
│   ├── dashboard.html          # Operations Dashboard & Trend Charts
│   ├── aqi.html                # AQI Gauge, Pollutants & Hotspot Map
│   ├── aqi_solutions.html      # Root-Cause Diagnostic & Mitigations
│   ├── simulator.html          # What-If Parameter Sliders & Live Preview
│   ├── results.html            # Before vs After Impact Dashboard
│   ├── map.html                # Interactive Leaflet GIS Risk Map
│   ├── reports.html            # Stored Scenarios & PDF Exports
│   └── about.html              # Architecture & Scientific Disclaimers
│
└── static/                     # Static Assets
    └── css/
        └── style.css           # Glassmorphism, Dark Mode & Climate Palette
```

---

## 🧮 Explainable AI & Simulation Logic

Risk scoring is computed using transparent, weighted multi-hazard equations:

$$\text{Exposure Score} = w_f \cdot S_{\text{flood}} + w_a \cdot S_{\text{aqi}} + w_h \cdot S_{\text{heat}} + w_w \cdot S_{\text{water}} + w_p \cdot S_{\text{power}} + \text{Synergy Bonus}$$

| Hazard Dimension | Default Weight | Key Indicator |
| :--- | :--- | :--- |
| **Flood Potential** | 30% | 24h Rainfall total vs. drainage capacity |
| **Air Quality (AQI)** | 25% | Observed AQI & particulate load |
| **Thermal Heat Stress**| 20% | Ambient temperature adjusted for relative humidity |
| **Water Stress** | 15% | Municipal storage & reservoir percentage |
| **Grid Power Outage** | 10% | Substation uptime & transformer strain |

**Compound Hazard Synergy:** When severe rainfall (>130mm) coincides with a power blackout (<60%), an automatic non-linear amplification penalty (+12 pts) is added because automated drainage pumps fail, severely elevating flood vulnerability.

---

## 🚀 Quick Setup & Run Instructions

### Prerequisites
- Python 3.9+ (tested with Python 3.12)
- pip

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
Visit: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/weather/<location>` | Returns current weather, AQI, and baseline risk. |
| `GET` | `/api/aqi/<location>` | Returns detailed pollutant telemetry and source attribution. |
| `POST`| `/api/simulate` | Executes What-If simulation with custom JSON parameters. |
| `POST`| `/api/scenarios/save` | Persists simulated scenario and results to SQLite database. |
| `GET` | `/api/scenarios` | Fetches list of all saved scenario records. |
| `GET` | `/api/scenario/<id>` | Fetches single scenario with full impact details. |
| `GET` | `/api/map-data` | Returns GeoJSON-style roads, infrastructure, and risk zones. |
| `POST`| `/api/recommendations` | Generates decision-support directives for given parameters. |
| `GET` | `/reports/download/<id>` | Generates and downloads formal PDF report. |

---

## 🛡️ Safety & Modelled Output Notice
All simulated outputs, road accessibility statuses, and population exposure figures in CLIMATEX are **modelled estimates** engineered for municipal contingency planning. They provide actionable decision support rather than guaranteed forecasts.
