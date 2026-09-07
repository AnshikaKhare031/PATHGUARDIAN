from unicodedata import category

from fastapi import FastAPI
from database.geospatial.spatial_queries import get_score_for_point,  get_reports_near, get_scores_for_points, insert_report
from pydantic import BaseModel
from typing import List, Tuple
class RoutePoints(BaseModel):   #basemodel: used for defining the exact shape of the data 
    points: List[Tuple[float, float]]
app = FastAPI()



@app.get("/")
def read_root():
    return {"message": "PathGuardian API is running"}

@app.get("/api/score")
def score(lat: float, lng: float):
    result = get_score_for_point(lat, lng)
    return {"lat": lat, "lng": lng, "score": result}

@app.get("/api/reports/nearby")
def reports_nearby(lat: float, lng: float, radius: float=1000):
    results = get_reports_near(lat, lng, radius)
    reports = [
        {"id": r[0], "category": r[1], "description": r[2], "reported_at": str(r[3])}
        for r in results
    ]

    return {"lat": lat, "lng": lng, "radius": radius, "reports": reports}

@app.post("/api/scores/route")
def scores_for_route(data: RoutePoints):
    results = get_scores_for_points(data.points)
    return {"scores": results}

class ReportInput(BaseModel):
    lat: float
    lng: float
    category: str
    description: str

@app.post("/api/reports")
def create_report(data: ReportInput):
    new_id = insert_report(data.lat, data.lng, data.category, data.description)
    return {"message": "Report created", "id": new_id}