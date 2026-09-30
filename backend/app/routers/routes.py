from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.scoring_engine import calculate_safety_score_for_point
from app.services.routing_service import get_route_alternatives

router = APIRouter()


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    lng: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")


class RouteRequest(BaseModel):
    start: Coordinates
    end: Coordinates


def _sample_points(geometry: list, num_samples: int = 5) -> list:
    """
    Picks a few evenly-spaced points along the route (not every single
    point - that would be too many calls) so we can score safety along
    the WHOLE route, not just the start and end.
    """
    if len(geometry) <= num_samples:
        return geometry
    step = max(1, len(geometry) // num_samples)
    return geometry[::step]


def _score_full_route(geometry: list) -> dict:
    """
    V1 approach: sample a handful of points along the route and average
    their individual safety scores. This is intentionally simple -
    good enough to demo, easy to explain in viva, and easy to upgrade
    later (e.g. weighting darker/emptier stretches more heavily).
    """
    sampled = _sample_points(geometry)
    scores = [
        calculate_safety_score_for_point(p["lat"], p["lng"])["safety_score"]
        for p in sampled
    ]
    avg_score = round(sum(scores) / len(scores), 1)
    return {"safety_score": avg_score, "sampled_points": len(sampled)}


def _pick_safest_route(routes: list) -> dict:
    """
    Compares route alternatives and picks the safest one - this is the
    core "don't just pick the shortest route" logic.

    V1 rule (simple, explainable, intentionally not over-engineered):
      1. Score every alternative route for safety.
      2. Find the shortest distance among all alternatives.
      3. Only consider routes that are not more than 50% longer than
         the shortest one (so we never suggest a silly 3x detour).
      4. Among those "reasonable" routes, pick the one with the
         highest safety score.

    Why this rule: Route A (2km, safety 85) vs Route B (1.5km, safety
    45) - Route A is only ~33% longer, well within the 50% limit, so
    we pick the safer Route A over the shorter Route B. This is a
    deliberately simple cost model - Safety Score -> Risk (inverse of
    safety) -> Routing Cost, done here as a straightforward filter +
    max-safety pick rather than a single combined formula, so it's
    easy to explain and tune.
    """
    scored_routes = []
    for route in routes:
        if "error" in route:
            continue
        safety_info = _score_full_route(route["geometry"])
        scored_routes.append({**route, **safety_info})

    if not scored_routes:
        # OSRM totally failed - fall back to whatever we got (straight line)
        return routes[0]

    shortest_distance = min(r["distance_km"] for r in scored_routes)
    max_allowed_distance = shortest_distance * 1.5

    reasonable_routes = [
        r for r in scored_routes if r["distance_km"] <= max_allowed_distance
    ]

    safest = max(reasonable_routes, key=lambda r: r["safety_score"])
    return safest


@router.post("/route")
async def get_safe_route(data: RouteRequest):
    try:
        start = {"lat": data.start.lat, "lng": data.start.lng}
        end = {"lat": data.end.lat, "lng": data.end.lng}

        if start == end:
            raise HTTPException(status_code=400, detail="Start and end points cannot be the same")

        alternatives = await get_route_alternatives(start, end)
        best_route = _pick_safest_route(alternatives)

        return {
            "route": {
                "geometry": best_route["geometry"],
                "distance_km": best_route["distance_km"],
                "duration_min": best_route.get("duration_min"),
                "safety_score": best_route.get("safety_score"),
            },
            "alternatives_considered": len(alternatives),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate route: {str(e)}")
