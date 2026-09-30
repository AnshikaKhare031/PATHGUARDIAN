import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import HeatmapLayer from "./HeatmapLayer";
import LegendControl from "./LegendControl";
import SafeRouteLayer from "./SafeRouteLayer";

const KANPUR_CENTER = [26.4499, 80.3319];

const DEMO_SAFETY_POINTS = [
  { id: 1, lat: 26.4548, lng: 80.3301, safetyScore: 0.9 },
  { id: 2, lat: 26.4521, lng: 80.3375, safetyScore: 0.75 },
  { id: 3, lat: 26.4466, lng: 80.3252, safetyScore: 0.65 },
  { id: 4, lat: 26.4587, lng: 80.3422, safetyScore: 0.45 },
  { id: 5, lat: 26.4438, lng: 80.3404, safetyScore: 0.3 },
  { id: 6, lat: 26.4485, lng: 80.3501, safetyScore: 0.2 },
  { id: 7, lat: 26.4389, lng: 80.3334, safetyScore: 0.15 },
  { id: 8, lat: 26.4612, lng: 80.3228, safetyScore: 0.8 }
];
const DEMO_SAFE_ROUTE = [
  [26.4389, 80.3334],
  [26.4425, 80.3358],
  [26.4466, 80.3371],
  [26.4513, 80.3395],
  [26.4587, 80.3422]
];
export default function MapView({
  safetyPoints = DEMO_SAFETY_POINTS,
  routeCoordinates = DEMO_SAFE_ROUTE
}) {
  return (
    <div
      style={{
        height: "70vh",
        minHeight: "500px",
        width: "100%",
        borderRadius: "12px",
        overflow: "hidden"
      }}
    >
      <MapContainer
        center={KANPUR_CENTER}
        zoom={13}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <HeatmapLayer safetyPoints={safetyPoints} />
        <LegendControl />
        <SafeRouteLayer routeCoordinates={routeCoordinates} />
      </MapContainer>
    </div>
  );
}