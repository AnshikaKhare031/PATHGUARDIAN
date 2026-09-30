import httpx

# Using the public OSRM demo server - no local Docker/OSRM setup needed.
# Good for development/demo; has rate limits, so we handle 429/503 below.
OSRM_BASE_URL = "https://router.project-osrm.org"


async def get_route_alternatives(start: dict, end: dict) -> list:
    """
    Calls the local OSRM server and asks for MULTIPLE route options
    (not just one), so we can later pick the SAFEST one instead of
    just the shortest one.

    Returns a list of routes, each with:
      - geometry (list of {lat, lng} points)
      - distance_km
      - duration_min
    """
    url = (
        f"{OSRM_BASE_URL}/route/v1/foot/"
        f"{start['lng']},{start['lat']};{end['lng']},{end['lat']}"
        f"?overview=full&geometries=geojson&alternatives=true"
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

        if response.status_code in (429, 503):
            # Public OSRM server is rate-limiting or temporarily overloaded -
            # fall back gracefully instead of crashing the whole request.
            raise Exception(f"OSRM server busy (status {response.status_code})")

        data = response.json()

        if data.get("code") != "Ok":
            raise Exception(f"OSRM error: {data.get('code')}")

        routes = []
        for route in data["routes"]:
            # GeoJSON gives [lng, lat] pairs -> convert to {lat, lng}
            coordinates = [
                {"lat": point[1], "lng": point[0]}
                for point in route["geometry"]["coordinates"]
            ]
            routes.append({
                "geometry": coordinates,
                "distance_km": round(route["distance"] / 1000, 2),
                "duration_min": round(route["duration"] / 60, 1),
            })

        return routes

    except Exception as e:
        # Fallback: if OSRM is down, return a straight line so the app
        # doesn't crash. Only one "route" in this fallback case.
        return [{
            "geometry": [start, end],
            "distance_km": 0.0,
            "duration_min": 0.0,
            "error": f"Routing engine unavailable: {str(e)}",
        }]


# Kept for backward compatibility with any old code that still calls
# get_real_route() directly (returns just the first/best route).
async def get_real_route(start: dict, end: dict) -> dict:
    alternatives = await get_route_alternatives(start, end)
    return alternatives[0]
