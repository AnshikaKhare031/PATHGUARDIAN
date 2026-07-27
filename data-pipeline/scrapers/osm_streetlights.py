import json
import logging
import os
import random
import requests
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# List of Overpass API endpoints for fallback
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]


def fetch_streetlights_by_city(city: str) -> List[Dict[str, Any]]:
    """
    Fetches streetlight nodes and lit road ways in Central Lucknow.
    """
    # Slightly broader Central Lucknow BBOX: 26.80 to 26.90 Lat | 80.90 to 81.00 Lon
    bbox = "26.80,80.90,26.90,81.00"

    query = f"""
    [out:json][timeout:25];
    (
      node["highway"="street_lamp"]({bbox});
      node["lit"="yes"]({bbox});
      way["lit"="yes"]({bbox});
    );
    out center;
    """

    logger.info(f"Querying Overpass API for lighting data in area ({bbox})...")

    # Cycle through endpoints until one responds
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://z.overpass-api.de/api/interpreter"
    ]

    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint,
                data={"data": query},
                headers={"User-Agent": "PathGuardian-App/1.0"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            elements = data.get("elements", [])
            if elements:
                logger.info(f"Successfully retrieved {len(elements)} lighting elements from {endpoint}.")
                return elements
        except requests.exceptions.RequestException as e:
            logger.warning(f"Endpoint {endpoint} failed/timed out, trying next...")

    logger.error("All Overpass endpoints failed or returned no data.")
    return []


def generate_synthetic_streetlights() -> List[Dict[str, Any]]:
    """
    Generates ~150 realistic streetlight nodes within Lucknow bounding box (26.80 to 26.90 Lat | 80.90 to 81.00 Lon).
    """
    logger.info("Generating ~150 synthetic streetlights as fallback...")
    synthetic_data = []
    random.seed(42)  # For deterministic generation
    
    # Generate points along simulated grid lines (latitudes/longitudes)
    lats = [26.81, 26.83, 26.85, 26.87, 26.89]
    lons = [80.91, 80.93, 80.95, 80.97, 80.99]
    
    node_id = 999000000
    
    for lat in lats:
        for i in range(15):
            lon = 80.90 + (i * 0.1 / 15) + random.uniform(-0.001, 0.001)
            synthetic_data.append({
                "id": node_id,
                "type": "node",
                "lat": round(lat + random.uniform(-0.0005, 0.0005), 6),
                "lon": round(lon, 6),
                "tags": {"highway": "street_lamp", "source": "synthetic_fallback"}
            })
            node_id += 1

    for lon in lons:
        for i in range(15):
            lat = 26.80 + (i * 0.1 / 15) + random.uniform(-0.001, 0.001)
            synthetic_data.append({
                "id": node_id,
                "type": "node",
                "lat": round(lat, 6),
                "lon": round(lon + random.uniform(-0.0005, 0.0005), 6),
                "tags": {"highway": "street_lamp", "source": "synthetic_fallback"}
            })
            node_id += 1

    logger.info(f"Generated {len(synthetic_data)} synthetic streetlight nodes.")
    return synthetic_data


def process_streetlight_data(raw_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned_data = []
    for element in raw_nodes:
        # Extract lat/lon whether it's a node or a way center
        lat = element.get("lat") or element.get("center", {}).get("lat")
        lon = element.get("lon") or element.get("center", {}).get("lon")

        if lat and lon:
            cleaned_data.append({
                "osm_id": element.get("id"),
                "latitude": lat,
                "longitude": lon,
                "signal_type": "streetlight",
                "weight": 1.0,
                "tags": element.get("tags", {})
            })

    logger.info(f"Processed {len(cleaned_data)} valid lighting points.")
    return cleaned_data


def save_to_json(data: List[Dict[str, Any]], output_filepath: str) -> None:
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info(f"Saved streetlight data to {output_filepath}")


def main():
    raw_nodes = fetch_streetlights_by_city("Lucknow")

    if not raw_nodes:
        logger.warning("No live streetlight nodes retrieved. Falling back to synthetic data.")
        raw_nodes = generate_synthetic_streetlights()

    processed_data = process_streetlight_data(raw_nodes)

    output_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "processed_streetlights.json"
    )
    save_to_json(processed_data, output_path)


if __name__ == "__main__":
    main()