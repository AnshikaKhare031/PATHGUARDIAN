import { useEffect } from "react";
import L from "leaflet";
import { useMap } from "react-leaflet";

export default function LegendControl() {
  const map = useMap();

  useEffect(() => {
    const legend = L.control({ position: "bottomright" });

    legend.onAdd = () => {
      const container = L.DomUtil.create("div");

      Object.assign(container.style, {
        background: "white",
        padding: "12px 14px",
        borderRadius: "8px",
        boxShadow: "0 2px 10px rgba(0, 0, 0, 0.2)",
        fontFamily: "Arial, sans-serif",
        fontSize: "14px",
        lineHeight: "1.8"
      });

      container.innerHTML = `
        <strong>Safety Level</strong><br />
        <span style="color:#22c55e;">●</span> Safe<br />
        <span style="color:#facc15;">●</span> Caution<br />
        <span style="color:#dc2626;">●</span> Risk
      `;

      L.DomEvent.disableClickPropagation(container);
      return container;
    };

    legend.addTo(map);

    return () => {
      legend.remove();
    };
  }, [map]);

  return null;
}