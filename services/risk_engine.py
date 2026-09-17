import numpy as np

class RiskEngine:
    """
    Explainable Risk and Environmental Impact Calculation Engine.
    Provides structured, transparent rule-based and weighted metric evaluations.
    Clearly marks all calculated indices as modelled/estimated metrics.
    """

    @staticmethod
    def evaluate_flood_risk(rainfall_mm):
        if rainfall_mm < 60.0:
            return "LOW", 25, "text-success", "badge-low", "#10B981"
        elif rainfall_mm < 110.0:
            return "MEDIUM", 55, "text-warning", "badge-medium", "#F59E0B"
        elif rainfall_mm < 180.0:
            return "HIGH", 82, "text-danger", "badge-high", "#EF4444"
        else:
            return "CRITICAL", 98, "text-purple", "badge-critical", "#7C3AED"

    @staticmethod
    def evaluate_heat_risk(temperature_c, humidity_pct=70.0):
        # Approximated Heat Index adjustment
        heat_index = temperature_c + 0.05 * (humidity_pct - 50)
        if heat_index < 32.0:
            return "LOW", 20, "text-success", "badge-low", "#10B981"
        elif heat_index < 39.0:
            return "MEDIUM", 50, "text-warning", "badge-medium", "#F59E0B"
        elif heat_index < 46.0:
            return "HIGH", 80, "text-danger", "badge-high", "#EF4444"
        else:
            return "CRITICAL", 96, "text-purple", "badge-critical", "#7C3AED"

    @staticmethod
    def evaluate_aqi_risk(aqi):
        if aqi <= 100:
            return "LOW", 20, "text-success", "badge-low", "#10B981"
        elif aqi <= 180:
            return "MEDIUM", 55, "text-warning", "badge-medium", "#F59E0B"
        elif aqi <= 280:
            return "HIGH", 84, "text-danger", "badge-high", "#EF4444"
        else:
            return "CRITICAL", 98, "text-purple", "badge-critical", "#7C3AED"

    @staticmethod
    def evaluate_water_risk(water_avail_pct):
        if water_avail_pct >= 75.0:
            return "LOW", 20, "text-success", "badge-low", "#10B981"
        elif water_avail_pct >= 50.0:
            return "MEDIUM", 50, "text-warning", "badge-medium", "#F59E0B"
        elif water_avail_pct >= 25.0:
            return "HIGH", 80, "text-danger", "badge-high", "#EF4444"
        else:
            return "CRITICAL", 95, "text-purple", "badge-critical", "#7C3AED"

    @staticmethod
    def evaluate_power_risk(power_avail_pct):
        if power_avail_pct >= 85.0:
            return "LOW", 15, "text-success", "badge-low", "#10B981"
        elif power_avail_pct >= 60.0:
            return "MEDIUM", 50, "text-warning", "badge-medium", "#F59E0B"
        elif power_avail_pct >= 35.0:
            return "HIGH", 80, "text-danger", "badge-high", "#EF4444"
        else:
            return "CRITICAL", 95, "text-purple", "badge-critical", "#7C3AED"

    def compute_multi_factor_risk(self, rainfall, temp, aqi, water_avail, power_avail, humidity=70.0):
        f_cat, f_score, _, _, _ = self.evaluate_flood_risk(rainfall)
        h_cat, h_score, _, _, _ = self.evaluate_heat_risk(temp, humidity)
        a_cat, a_score, _, _, _ = self.evaluate_aqi_risk(aqi)
        w_cat, w_score, _, _, _ = self.evaluate_water_risk(water_avail)
        p_cat, p_score, _, _, _ = self.evaluate_power_risk(power_avail)

        # Base weights: Flood 30%, Heat 20%, AQI 25%, Water 15%, Power 10%
        weights = np.array([0.30, 0.20, 0.25, 0.15, 0.10])
        scores = np.array([f_score, h_score, a_score, w_score, p_score])

        weighted_score = np.dot(weights, scores)

        # Multi-factor compound hazards amplification:
        # e.g. Heavy Rain + Power Outage compound risk!
        synergy_bonus = 0.0
        if rainfall > 130 and power_avail < 60:
            synergy_bonus += 12.0  # Inundation during grid failure severely blocks pumps & response
        if temp > 38 and water_avail < 45:
            synergy_bonus += 10.0  # Extreme heat during drought

        # If two or more major hazards are HIGH/CRITICAL, elevate exposure score
        high_count = sum(1 for c in [f_cat, h_cat, a_cat, w_cat, p_cat] if c in ['HIGH', 'CRITICAL'])
        if high_count >= 2:
            synergy_bonus += 6.0

        exposure_score = min(100.0, round(float(weighted_score + synergy_bonus), 1))

        if exposure_score < 30.0:
            overall_cat = "LOW"
            badge_class = "badge-low"
            text_class = "text-success"
            color_hex = "#10B981"
        elif exposure_score < 60.0:
            overall_cat = "MEDIUM"
            badge_class = "badge-medium"
            text_class = "text-warning"
            color_hex = "#F59E0B"
        elif exposure_score < 85.0:
            overall_cat = "HIGH"
            badge_class = "badge-high"
            text_class = "text-danger"
            color_hex = "#EF4444"
        else:
            overall_cat = "CRITICAL"
            badge_class = "badge-critical"
            text_class = "text-purple"
            color_hex = "#7C3AED"

        contributors = [
            {'factor': 'Rainfall (Flood Potential)', 'category': f_cat, 'score': f_score, 'weight': '30%'},
            {'factor': 'Air Quality Index (AQI)', 'category': a_cat, 'score': a_score, 'weight': '25%'},
            {'factor': 'Temperature (Thermal Stress)', 'category': h_cat, 'score': h_score, 'weight': '20%'},
            {'factor': 'Water Availability', 'category': w_cat, 'score': w_score, 'weight': '15%'},
            {'factor': 'Power Grid Availability', 'category': p_cat, 'score': p_score, 'weight': '10%'}
        ]

        contributors.sort(key=lambda x: x['score'], reverse=True)

        return {
            'overall_risk': overall_cat,
            'exposure_score': exposure_score,
            'badge_class': badge_class,
            'text_class': text_class,
            'color_hex': color_hex,
            'flood_risk': f_cat,
            'heat_risk': h_cat,
            'air_quality_risk': a_cat,
            'water_risk': w_cat,
            'power_risk': p_cat,
            'contributors': contributors,
            'synergy_active': synergy_bonus > 0
        }
