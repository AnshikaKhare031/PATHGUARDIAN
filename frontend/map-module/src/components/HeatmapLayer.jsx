import { useEffect } from "react";
import L from "leaflet";
import { useMap } from "react-leaflet";
import "leaflet.heat";

export default function HeatmapLayer({ safetyPoints = [] }) {
  const map = useMap();

  useEffect(() => {
    const heatPoints = safetyPoints
      .filter(
        (point) =>
          Number.isFinite(point.lat) &&
          Number.isFinite(point.lng) &&
          Number.isFinite(point.safetyScore)
      )
      .map((point) => {
        const riskIntensity = Math.max(
          0.1,
          Math.min(1, 1 - point.safetyScore)
        );

        return [point.lat, point.lng, riskIntensity];
      });

    if (heatPoints.length === 0) {
      return undefined;
    }

    const heatLayer = L.heatLayer(heatPoints, {
      radius: 35,
      blur: 28,
      maxZoom: 17,
      minOpacity: 0.35,
      gradient: {
        0.2: "#22c55e",
        0.55: "#facc15",
        0.8: "#f97316",
        1: "#dc2626"
      }
    }).addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [map, safetyPoints]);

  return null;
}