from fastapi import APIRouter
from pydantic import BaseModel
from app.services.scoring_engine import score_route

router = APIRouter()

class Coordinates(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Coordinates
    end: Coordinates

@router.post("/route")
def get_safe_route(data: RouteRequest):
    start = {"lat": data.start.lat, "lng": data.start.lng}
    end = {"lat": data.end.lat, "lng": data.end.lng}

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