import logging
from typing import Dict, Any
from app.services.proxy_data_service import proxy_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def calculate_safety_score_for_point(lat: float, lon: float) -> Dict[str, Any]:
    """Calculates the proximity-based safety score for a given coordinate."""
    nearby_signals = proxy_service.get_nearby_signals(lat, lon, radius_km=0.5)

    # Initialize counts
    streetlight_count = 0
    police_station_count = 0
    foot_traffic_weights = []
    incident_count = 0

    for signal in nearby_signals:
        sig_type = signal.get("signal_type")
        if sig_type == "streetlight":
            streetlight_count += 1
        elif sig_type == "police_station":
            police_station_count += 1
        elif sig_type == "foot_traffic":
            weight = signal.get("weight")
            if weight is not None:
                foot_traffic_weights.append(float(weight))
        elif sig_type == "user_report":
            incident_count += 1

    # 1. Lighting score: min(100.0, streetlight_count * 20.0 + 30.0)
    lighting_score = min(100.0, streetlight_count * 20.0 + 30.0)

    # 2. Police score: 100.0 if police_station_count > 0 else 40.0
    police_score = 100.0 if police_station_count > 0 else 40.0

    # 3. Foot traffic score: average weight of foot traffic signals * 100.0 (default 50.0)
    if foot_traffic_weights:
        foot_traffic_score = (sum(foot_traffic_weights) / len(foot_traffic_weights)) * 100.0
    else:
        foot_traffic_score = 50.0

    # 4. Incident penalty: incident_count * 15.0
    incident_penalty = incident_count * 15.0

    # Compute weighted final score: (Lighting * 0.35) + (Police * 0.30) + (Traffic * 0.20) - Penalty
    # Clamped between 10.0 and 100.0.
    raw_score = (lighting_score * 0.35) + (police_score * 0.30) + (foot_traffic_score * 0.20) - incident_penalty
    safety_score = max(10.0, min(100.0, raw_score))

    return {
        "safety_score": round(safety_score, 1),
        "breakdown": {
            "lighting": round(lighting_score, 1),
            "police": round(police_score, 1),
            "foot_traffic": round(foot_traffic_score, 1),
            "incident_penalty": round(incident_penalty, 1)
        },
        "signals_count": {
            "streetlight": streetlight_count,
            "police_station": police_station_count,
            "foot_traffic": len(foot_traffic_weights),
            "user_report": incident_count
        }
    }


def score_route(start: dict, end: dict) -> dict:
    """Calculates average safety score between start and end coordinates."""
    # Note: start and end dicts may use 'lng' instead of 'lon'
    start_lat = start.get("lat")
    start_lon = start.get("lng") if start.get("lng") is not None else start.get("lon")
    
    end_lat = end.get("lat")
    end_lon = end.get("lng") if end.get("lng") is not None else end.get("lon")

    start_score_data = calculate_safety_score_for_point(start_lat, start_lon)
    end_score_data = calculate_safety_score_for_point(end_lat, end_lon)

    avg_score = round((start_score_data["safety_score"] + end_score_data["safety_score"]) / 2.0, 1)
    
    avg_breakdown = {
        "lighting": round((start_score_data["breakdown"]["lighting"] + end_score_data["breakdown"]["lighting"]) / 2.0, 1),
        "police": round((start_score_data["breakdown"]["police"] + end_score_data["breakdown"]["police"]) / 2.0, 1),
        "foot_traffic": round((start_score_data["breakdown"]["foot_traffic"] + end_score_data["breakdown"]["foot_traffic"]) / 2.0, 1),
        "incident_penalty": round((start_score_data["breakdown"]["incident_penalty"] + end_score_data["breakdown"]["incident_penalty"]) / 2.0, 1)
    }

    combined_signals_count = {
        key: start_score_data["signals_count"][key] + end_score_data["signals_count"][key]
        for key in start_score_data["signals_count"]
    }

    return {
        "safety_score": avg_score,
        "breakdown": avg_breakdown,
        "signals_count": combined_signals_count
    }


# Alias for compatibility with routers/score.py
calculate_location_score = calculate_safety_score_for_point