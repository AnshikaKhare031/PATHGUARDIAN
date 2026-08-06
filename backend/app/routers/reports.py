from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()

reports_db = []


class ReportRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    safety_rating: int = Field(..., ge=1, le=5, description="1 = very unsafe, 5 = very safe")
    comment: str = Field(default="", max_length=500)


@router.post("/reports")
def submit_report(data: ReportRequest):
    try:
        report = {
            "id": len(reports_db) + 1,
            "lat": data.lat,
            "lng": data.lng,
            "safety_rating": data.safety_rating,
            "comment": data.comment.strip(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        reports_db.append(report)
        return {"message": "Report submitted successfully", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit report: {str(e)}")


@router.get("/reports")
def get_all_reports():
    return {"reports": reports_db, "count": len(reports_db)}