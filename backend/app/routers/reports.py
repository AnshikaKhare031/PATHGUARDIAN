from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

reports_db = []


class ReportRequest(BaseModel):
    lat: float
    lng: float
    safety_rating: int
    comment: str = ""


@router.post("/reports")
def submit_report(data: ReportRequest):
    if not (1 <= data.safety_rating <= 5):
        return {"error": "safety_rating must be between 1 and 5"}

    report = {
        "id": len(reports_db) + 1,
        "lat": data.lat,
        "lng": data.lng,
        "safety_rating": data.safety_rating,
        "comment": data.comment,
        "timestamp": datetime.utcnow().isoformat(),
    }
    reports_db.append(report)

    return {"message": "Report submitted successfully", "report": report}


@router.get("/reports")
def get_all_reports():
    return {"reports": reports_db, "count": len(reports_db)}