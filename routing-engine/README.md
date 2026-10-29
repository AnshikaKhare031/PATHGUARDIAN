# Routing Engine

PathGuardian recommends the **safest practical walking route**, not just the shortest one.

## How it works
Code lives in the backend (not in this folder):

- `backend/app/services/routing_service.py` - calls OSRM and asks for several walking routes (`alternatives=true`).
- `backend/app/routers/routes.py` - scores each route for safety and picks the best one.

Flow: `POST /api/route` -> OSRM alternatives -> sample 5 points along each route -> safety score per point
(`scoring_engine.calculate_safety_score_for_point`) -> average -> choose the safest route that is not more than
50% longer than the shortest alternative.

## OSRM server
The public demo server `https://router.project-osrm.org` is used (no Docker or local setup needed).
It is rate limited; on HTTP 429/503 or any OSRM error the service returns a straight start-end line with an
`error` field, and `/api/route` adds a `warning` to its response instead of crashing.

To use your own OSRM server, change `OSRM_BASE_URL` in `routing_service.py`.

## API
`POST /api/route`

Request:
```json
{ "start": {"lat": 26.4499, "lng": 80.3319}, "end": {"lat": 26.4670, "lng": 80.3462} }
```

Response (`routes[0]` and `route` are the same object):
```json
{
  "routes": [ { "geometry": [{"lat": 0, "lng": 0}], "distance_km": 2.1, "duration_min": 25.0,
                "safety_score": 33.7,
                "breakdown": {"lighting": 33.3, "police": 40.0, "foot_traffic": 50.0, "incident_penalty": 0.0} } ],
  "route": { "...same as routes[0]..." },
  "alternatives_considered": 2
}
```
Errors: `400` same start/end, `422` invalid coordinates, `500` unexpected failure.

## Tests
From `backend/`: `python -m pytest tests -v` (OSRM is mocked, runs offline).

## Not implemented (future work)
`client/`, `cost-profile/safety_weighted_profile.lua` and `osrm-setup/` are empty placeholders for a self-hosted OSRM
with a custom safety cost profile. V1 uses the public server and picks among alternatives instead.
