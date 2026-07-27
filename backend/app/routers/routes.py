from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Coordinates(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Coordinates
    end: Coordinates

@router.post("/route")
def get_safe_route(data: RouteRequest):
    dummy_score = 82

    return {
        "routes": [
            {
                "geometry": [
                    {"lat": data.start.lat, "lng": data.start.lng},
                    {"lat": data.end.lat, "lng": data.end.lng}
                ],
                "distance_km": 3.5,
                "safety_score": dummy_score,
                "breakdown": {
                    "lighting": 85,
                    "police_proximity": 78,
                    "crime_risk": 80,
                    "user_reports": 90
                }
            }
        ]
    }