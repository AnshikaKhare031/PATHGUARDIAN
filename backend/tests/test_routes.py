"""
Tests for POST /api/route (safest-route selection).

OSRM is mocked, so these tests run offline. Run from the backend folder:
    pip install pytest httpx
    python -m pytest tests -v
"""
from fastapi.testclient import TestClient

from app.main import app
from app.routers import routes as routes_module

client = TestClient(app)

START = {"lat": 26.4499, "lng": 80.3319}
END = {"lat": 26.4670, "lng": 80.3462}


def _line(lat0, lng0, lat1, lng1, n=10):
    return [
        {"lat": lat0 + (lat1 - lat0) * i / (n - 1), "lng": lng0 + (lng1 - lng0) * i / (n - 1)}
        for i in range(n)
    ]


def _mock_osrm(monkeypatch, routes):
    async def fake(start, end):
        return routes

    monkeypatch.setattr(routes_module, "get_route_alternatives", fake)


def _mock_scores(monkeypatch, score_by_lng_threshold):
    """Points with lng below the threshold score 80, others 40."""

    def fake_score(lat, lng):
        s = 80.0 if lng < score_by_lng_threshold else 40.0
        return {"safety_score": s, "breakdown": {"lighting": s, "police": s, "foot_traffic": s, "incident_penalty": 0.0}}

    monkeypatch.setattr(routes_module, "calculate_safety_score_for_point", fake_score)


def test_same_start_and_end_returns_400():
    r = client.post("/api/route", json={"start": START, "end": START})
    assert r.status_code == 400


def test_invalid_latitude_returns_422():
    r = client.post("/api/route", json={"start": {"lat": 200, "lng": 80.3}, "end": END})
    assert r.status_code == 422


def test_missing_end_returns_422():
    r = client.post("/api/route", json={"start": START})
    assert r.status_code == 422


def test_picks_safer_route_within_detour_limit(monkeypatch):
    short_unsafe = {"geometry": _line(26.45, 80.40, 26.46, 80.41), "distance_km": 1.5, "duration_min": 18.0}
    longer_safe = {"geometry": _line(26.45, 80.30, 26.46, 80.31), "distance_km": 2.0, "duration_min": 24.0}
    _mock_osrm(monkeypatch, [short_unsafe, longer_safe])
    _mock_scores(monkeypatch, 80.35)

    body = client.post("/api/route", json={"start": START, "end": END}).json()
    assert body["route"]["distance_km"] == 2.0
    assert body["route"]["safety_score"] == 80.0
    assert body["alternatives_considered"] == 2
    assert body["routes"][0] == body["route"]
    assert set(body["route"]["breakdown"]) == {"lighting", "police", "foot_traffic", "incident_penalty"}


def test_rejects_safer_route_that_is_too_long(monkeypatch):
    short_unsafe = {"geometry": _line(26.45, 80.40, 26.46, 80.41), "distance_km": 1.0, "duration_min": 12.0}
    way_longer_safe = {"geometry": _line(26.45, 80.30, 26.46, 80.31), "distance_km": 1.6, "duration_min": 19.0}
    _mock_osrm(monkeypatch, [short_unsafe, way_longer_safe])
    _mock_scores(monkeypatch, 80.35)

    body = client.post("/api/route", json={"start": START, "end": END}).json()
    assert body["route"]["distance_km"] == 1.0  # 1.6 km is 60% longer -> not allowed


def test_osrm_down_returns_fallback_with_warning(monkeypatch):
    fallback = [{
        "geometry": [START, END],
        "distance_km": 0.0,
        "duration_min": 0.0,
        "error": "Routing engine unavailable: boom",
    }]
    _mock_osrm(monkeypatch, fallback)

    r = client.post("/api/route", json={"start": START, "end": END})
    assert r.status_code == 200
    body = r.json()
    assert "warning" in body
    assert body["route"]["geometry"] == [START, END]


def test_sampling_includes_first_and_last_point():
    geometry = _line(26.45, 80.30, 26.46, 80.31, n=37)
    sampled = routes_module._sample_points(geometry)
    assert sampled[0] == geometry[0]
    assert sampled[-1] == geometry[-1]
