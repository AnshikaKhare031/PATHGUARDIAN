import { CircleMarker, Polyline, Popup } from "react-leaflet";

export default function SafeRouteLayer({ routeCoordinates = [] }) {
  if (!Array.isArray(routeCoordinates) || routeCoordinates.length < 2) {
    return null;
  }

  const startPoint = routeCoordinates[0];
  const endPoint = routeCoordinates[routeCoordinates.length - 1];

  return (
    <>
      <Polyline
        positions={routeCoordinates}
        pathOptions={{
          color: "white",
          weight: 9,
          opacity: 0.9
        }}
      />

      <Polyline
        positions={routeCoordinates}
        pathOptions={{
          color: "#2563eb",
          weight: 5,
          opacity: 1
        }}
      />

      <CircleMarker
        center={startPoint}
        radius={8}
        pathOptions={{
          color: "white",
          fillColor: "#16a34a",
          fillOpacity: 1,
          weight: 3
        }}
      >
        <Popup>Route start</Popup>
      </CircleMarker>

      <CircleMarker
        center={endPoint}
        radius={8}
        pathOptions={{
          color: "white",
          fillColor: "#dc2626",
          fillOpacity: 1,
          weight: 3
        }}
      >
        <Popup>Route destination</Popup>
      </CircleMarker>
    </>
  );
}