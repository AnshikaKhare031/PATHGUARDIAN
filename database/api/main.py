from fastapi import FastAPI
from database.geospatial.spatial_queries import get_score_for_point,  get_score_for_point
app = FastAPI()



@app.get("/")
def read_root():
    return {"message": "PathGuardian API is running"}

@app.get("/api/score")
def score(lat: float, lng: float):
    result = get_score_for_point(lat, lng)
    return {"lat": lat, "lng": lng, "score": result}