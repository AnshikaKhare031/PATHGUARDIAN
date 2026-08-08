import httpx

OSRM_BASE_URL = "http://localhost:5000"


async def get_real_route(start: dict, end: dict) -> dict:
    """
    Calls the local OSRM server to get a real walking route.
    Returns geometry (list of lat/lng points), distance in km, and duration in minutes.
    """
    url = (
        f"{OSRM_BASE_URL}/route/v1/foot/"
        f"{start['lng']},{start['lat']};{end['lng']},{end['lat']}"
        f"?overview=full&geometries=geojson"
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            data = response.json()

        if data.get("code") != "Ok":
            raise Exception(f"OSRM error: {data.get('code')}")

        route = data["routes"][0]

        # GeoJSON gives [lng, lat] pairs — convert to our {lat, lng} format
        coordinates = [
            {"lat": point[1], "lng": point[0]}
            for point in route["geometry"]["coordinates"]
        ]

        return {
            "geometry": coordinates,
            "distance_km": round(route["distance"] / 1000, 2),
            "duration_min": round(route["duration"] / 60, 1),
        }

    except Exception as e:
        # Fallback: if OSRM is down, return a straight line so the app doesn't crash
        return {
            "geometry": [start, end],
            "distance_km": 0.0,
            "duration_min": 0.0,
            "error": f"Routing engine unavailable: {str(e)}"
        }