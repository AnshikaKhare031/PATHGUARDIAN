import json
import logging
import math
import os
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the great-circle distance between two points in kilometers."""
    # Earth radius in kilometers
    R = 6371.0
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c


class ProxyDataService:
    def __init__(self):
        self.signals: List[Dict[str, Any]] = []
        self._load_data()
        
    def _load_data(self):
        # Resolve target and fallback paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(current_dir)
        project_root = os.path.dirname(app_dir)
        
        target_paths = [
            os.path.join(app_dir, "data", "proxy_signals_kanpur.json"),
            os.path.join(project_root, "backend", "app", "data", "proxy_signals_kanpur.json")
        ]
        
        fallback_paths = [
            os.path.join(app_dir, "data", "mock_proxy_signals_kanpur.json"),
            os.path.join(project_root, "backend", "data", "mock_proxy_signals_kanpur.json"),
            os.path.join(project_root, "backend", "app", "data", "mock_proxy_signals_kanpur.json")
        ]
        
        # Try loading target paths
        for path in target_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.signals = json.load(f)
                    logger.info(f"Loaded {len(self.signals)} proxy signals from {path}")
                    return
                except Exception as e:
                    logger.error(f"Error loading {path}: {e}")
                    
        # Try loading fallback paths
        for path in fallback_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.signals = json.load(f)
                    logger.info(f"Loaded {len(self.signals)} fallback proxy signals from {path}")
                    return
                except Exception as e:
                    logger.error(f"Error loading fallback {path}: {e}")
                    
        logger.error("Failed to load any proxy signals dataset or fallback mock dataset.")
        self.signals = []

    def get_nearby_signals(self, lat: float, lon: float, radius_km: float = 0.5) -> List[Dict[str, Any]]:
        """Filters and returns all proxy signals within radius_km."""
        nearby = []
        for signal in self.signals:
            sig_lat = signal.get("latitude")
            sig_lon = signal.get("longitude")
            if sig_lat is not None and sig_lon is not None:
                dist = haversine_distance(lat, lon, float(sig_lat), float(sig_lon))
                if dist <= radius_km:
                    # Append distance info to the signal for convenience
                    signal_copy = signal.copy()
                    signal_copy["distance_km"] = round(dist, 4)
                    nearby.append(signal_copy)
        return nearby


# Create a single global instance ready to be imported
proxy_service = ProxyDataService()
