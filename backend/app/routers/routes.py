from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.scoring_engine import score_route
from app.services.routing_service import get_real_route

router = APIRouter()

class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    lng: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")

class RouteRequest(BaseModel):
    start: Coordinates
    end: Coordinates

@router.post("/route")
async def get_safe_route(data: RouteRequest):
    try:
        start = {"lat": data.start.lat, "lng": data.start.lng}
        end = {"lat": data.end.lat, "lng": data.end.lng}

        if start == end:
            raise HTTPException(status_code=400, detail="Start and end points cannot be the same")

        route_data = await get_real_route(start, end)
        score_data = score_route(start, end)

        return {
            "routes": [
                {
                    "geometry": route_data["geometry"],
                    "distance_km": route_data["distance_km"],
                    "duration_min": route_data.get("duration_min"),
                    "safety_score": score_data["safety_score"],
                    "breakdown": score_data["breakdown"],
                }
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate route: {str(e)}")