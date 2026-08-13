from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import routes, reports, score

app = FastAPI(title="PathGuardian Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(routes.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(score.router, prefix="/api", tags=["Score"])