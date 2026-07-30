from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.scoring_engine import score_route

router = APIRouter()

class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    lng: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")

class RouteRequest(BaseModel):
    start: Coordinates
    end: Coordinates

@router.post("/route")
def get_safe_route(data: RouteRequest):
    try:
        start = {"lat": data.start.lat, "lng": data.start.lng}
        end = {"lat": data.end.lat, "lng": data.end.lng}

        if start == end:
            raise HTTPException(status_code=400, detail="Start and end points cannot be the same")

        result = score_route(start, end)

        return {
            "routes": [
                {
                    "geometry": [start, end],
                    "distance_km": 3.5,
                    "safety_score": result["safety_score"],
                    "breakdown": result["breakdown"],
                }
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate route: {str(e)}")