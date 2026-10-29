from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.scoring_engine import calculate_safety_score_for_point
from app.services.routing_service import get_route_alternatives

router = APIRouter()

# A route may be at most this much longer than the shortest alternative
# (1.5 = 50% longer) to still be considered "reasonable".
MAX_DETOUR_FACTOR = 1.5
# Number of evenly spaced points sampled along a route for safety scoring.
NUM_SAMPLES = 5


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    lng: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")


class RouteRequest(BaseModel):
    start: Coordinates
    end: Coordinates


def _sample_points(geometry: list, num_samples: int = NUM_SAMPLES) -> list:
    """
    Picks evenly spaced points along the route (always including the first
    and the last point) so safety is scored along the WHOLE route, not just
    at the start and end.
    """
    if len(geometry) <= num_samples:
        return geometry
    step = max(1, len(geometry) // num_samples)
    sampled = geometry[::step]
    if sampled[-1] != geometry[-1]:
        sampled.append(geometry[-1])
    return sampled


def _score_full_route(geometry: list) -> dict:
    """
    V1 approach: sample a handful of points along the route and average
    their safety scores and score breakdowns.
    """
    sampled = _sample_points(geometry)
    results = [calculate_safety_score_for_point(p["lat"], p["lng"]) for p in sampled]

    n = len(results)
    avg_score = round(sum(r["safety_score"] for r in results) / n, 1)
    breakdown_keys = results[0]["breakdown"].keys()
    avg_breakdown = {
        key: round(sum(r["breakdown"][key] for r in results) / n, 1)
        for key in breakdown_keys
    }
    return {
        "safety_score": avg_score,
        "breakdown": avg_breakdown,
        "sampled_points": n,
    }


def _pick_safest_route(routes: list) -> dict:
    """
    Compares route alternatives and picks the safest one.

    Rule (simple and explainable):
      1. Score every alternative route for safety.
      2. Find the shortest distance among the alternatives.
      3. Keep only routes not more than 50% longer than the shortest one.
      4. Among those, pick the one with the highest safety score.
    Returns (best_route, all_scored_routes).
    """
    scored_routes = []
    for route in routes:
        if "error" in route:
            continue
        scored_routes.append({**route, **_score_full_route(route["geometry"])})

    if not scored_routes:
        # OSRM failed completely: nothing to score, return the fallback line.
        return routes[0], []

    shortest = min(r["distance_km"] for r in scored_routes)
    reasonable = [r for r in scored_routes if r["distance_km"] <= shortest * MAX_DETOUR_FACTOR]
    best = max(reasonable, key=lambda r: r["safety_score"])
    return best, scored_routes


def _public_route(route: dict) -> dict:
    return {
        "geometry": route["geometry"],
        "distance_km": route["distance_km"],
        "duration_min": route.get("duration_min"),
        "safety_score": route.get("safety_score"),
        "breakdown": route.get("breakdown"),
    }


@router.post("/route")
async def get_safe_route(data: RouteRequest):
    try:
        start = {"lat": data.start.lat, "lng": data.start.lng}
        end = {"lat": data.end.lat, "lng": data.end.lng}

        if start == end:
            raise HTTPException(status_code=400, detail="Start and end points cannot be the same")

        alternatives = await get_route_alternatives(start, end)
        best, scored = _pick_safest_route(alternatives)
        selected = _public_route(best)

        response = {
            # Original response shape (list) kept so existing frontend code works.
            "routes": [selected],
            # Convenience single-route key.
            "route": selected,
            "alternatives_considered": len(alternatives),
        }
        if "error" in best:
            response["warning"] = best["error"]
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate route: {str(e)}")
