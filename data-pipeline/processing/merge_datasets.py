import json
import logging
import os
from collections import Counter
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_json_file(filepath: str) -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return []
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                logger.info(f"Successfully loaded {len(data)} records from {filepath}")
                return data
            else:
                logger.warning(f"Unexpected JSON structure in {filepath} (expected list of dicts)")
                return []
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return []


def validate_and_normalize(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    valid_records = []
    required_fields = {"latitude", "longitude", "signal_type", "weight", "source"}
    
    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        
        # Check if all required fields are present
        if not required_fields.issubset(record.keys()):
            continue
        
        lat = record.get("latitude")
        lon = record.get("longitude")
        
        # Skip records missing latitude or longitude
        if lat is None or lon is None:
            continue
        
        try:
            lat_val = round(float(lat), 6)
            lon_val = round(float(lon), 6)
            
            # Normalize record
            normalized_record = {
                "latitude": lat_val,
                "longitude": lon_val,
                "signal_type": str(record.get("signal_type")),
                "weight": float(record.get("weight")),
                "source": str(record.get("source"))
            }
            
            # Carry over optional name field if present
            if "name" in record:
                normalized_record["name"] = str(record["name"])
            # Carry over category if present (e.g. for user_reports)
            if "category" in record:
                normalized_record["category"] = str(record["category"])
                
            valid_records.append(normalized_record)
        except (ValueError, TypeError) as e:
            # Skip records with invalid data types
            continue
            
    return valid_records


def deduplicate_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    deduplicated = []
    
    for record in records:
        # Deduplicate if lat, lon (rounded to 6 decimals) and signal_type match
        key = (record["latitude"], record["longitude"], record["signal_type"])
        if key not in seen:
            seen.add(key)
            deduplicated.append(record)
            
    logger.info(f"Deduplication: {len(records)} records reduced to {len(deduplicated)} records.")
    return deduplicated


def main():
    # Resolve paths relative to project root (parent of data-pipeline)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # Input paths to check
    input_paths = [
        os.path.join(project_root, "data-pipeline", "processed_streetlights.json"),
        os.path.join(project_root, "data-pipeline", "processed_police_stations.json"),
        os.path.join(project_root, "backend", "data", "mock_proxy_signals_kanpur.json"),
        os.path.join(project_root, "backend", "app", "data", "mock_proxy_signals_kanpur.json"),
        os.path.join(project_root, "data-pipeline", "mock_proxy_signals_kanpur.json")
    ]
    
    all_raw_records = []
    for path in input_paths:
        records = load_json_file(path)
        all_raw_records.extend(records)
        
    # Validate and normalize
    valid_records = validate_and_normalize(all_raw_records)
    
    # Deduplicate
    final_records = deduplicate_records(valid_records)
    
    # Export targets
    output_path_1 = os.path.join(project_root, "data-pipeline", "processed_signals", "proxy_signals_kanpur.json")
    output_path_2 = os.path.join(project_root, "backend", "app", "data", "proxy_signals_kanpur.json")
    
    for out_path in [output_path_1, output_path_2]:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(final_records, f, indent=2)
            logger.info(f"Successfully exported dataset to {out_path}")
        except Exception as e:
            logger.error(f"Failed to write to {out_path}: {e}")
            
    # Breakdown statistics
    type_counter = Counter(r["signal_type"] for r in final_records)
    source_counter = Counter(r["source"] for r in final_records)
    
    logger.info("--- MERGED DATASET SUMMARY BREAKDOWN ---")
    logger.info(f"Total merged records: {len(final_records)}")
    logger.info("By Signal Type:")
    for sig_type, count in type_counter.items():
        logger.info(f"  - {sig_type}: {count}")
    logger.info("By Source:")
    for src, count in source_counter.items():
        logger.info(f"  - {src}: {count}")
    logger.info("----------------------------------------")


if __name__ == "__main__":
    main()
