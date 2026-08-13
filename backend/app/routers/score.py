from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.scoring_engine import calculate_location_score

router = APIRouter()

class ScoreRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude must be between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude must be between -180 and 180")

@router.post("/score")
async def get_score(payload: ScoreRequest):
    try:
        score_result = calculate_location_score(payload.latitude, payload.longitude)
        return score_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate score: {str(e)}")
