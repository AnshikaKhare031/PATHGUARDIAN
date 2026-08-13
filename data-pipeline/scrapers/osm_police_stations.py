import json
import logging
import os
import requests
from typing import Dict, List, Any, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# City Bounding Box: Kanpur, India (South: 26.40, West: 80.28, North: 26.55, East: 80.42)
KANPUR_BBOX = (26.40, 80.28, 26.55, 80.42)

OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"


def fetch_police_stations_by_bbox(bbox: Tuple[float, float, float, float]) -> List[Dict[str, Any]]:
    """Fetches police station nodes/ways within Kanpur bbox."""
    bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
    query = f"""
    [out:json][timeout:90];
    (
      node["amenity"="police"]({bbox_str});
      way["amenity"="police"]({bbox_str});
    );
    out center;
    """

    logger.info(f"Querying Overpass API for Kanpur police stations ({bbox_str})...")

    try:
        response = requests.post(
            OVERPASS_ENDPOINT,
            data={"data": query},
            headers={"User-Agent": "PathGuardian-App/1.0"},
            timeout=100
        )
        response.raise_for_status()
        data = response.json()
        elements = data.get("elements", [])
        if elements:
            logger.info(f"Retrieved {len(elements)} police station elements from {OVERPASS_ENDPOINT}.")
            return elements
        else:
            logger.warning(f"Overpass API returned 0 elements.")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Overpass API query failed: {e}")
        raise e


def process_police_data(raw_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned_data = []
    for element in raw_nodes:
        lat = element.get("lat") or element.get("center", {}).get("lat")
        lon = element.get("lon") or element.get("center", {}).get("lon")
        tags = element.get("tags", {})
        station_name = tags.get("name", "Police Station")

        if lat is not None and lon is not None:
            cleaned_data.append({
                "latitude": round(float(lat), 6),
                "longitude": round(float(lon), 6),
                "signal_type": "police_station",
                "weight": 1.0,
                "name": station_name,
                "source": "osm"
            })

    logger.info(f"Processed {len(cleaned_data)} valid police station points for Kanpur.")
    return cleaned_data


def save_to_json(data: List[Dict[str, Any]], output_filepath: str) -> None:
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved {len(data)} records to {output_filepath}")


def main():
    try:
        raw_nodes = fetch_police_stations_by_bbox(KANPUR_BBOX)
        if not raw_nodes:
            logger.error("No police station data retrieved for Kanpur. Terminating execution gracefully.")
            return
        
        processed_data = process_police_data(raw_nodes)
        
        output_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "processed_police_stations.json"
        )
        save_to_json(processed_data, output_path)
    except Exception as e:
        logger.error(f"Execution failed due to error: {e}. Gracefully terminating.")


if __name__ == "__main__":
    main()
