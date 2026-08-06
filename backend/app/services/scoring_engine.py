WEIGHTS = {
    "lighting": 0.35,
    "police_proximity": 0.30,
    "crime_risk": 0.20,
    "user_reports": 0.15,
}


def calculate_safety_score(lighting: float, police_proximity: float,
                            crime_risk: float, user_reports: float) -> dict:
    safety_score = (
        lighting * WEIGHTS["lighting"] +
        police_proximity * WEIGHTS["police_proximity"] +
        crime_risk * WEIGHTS["crime_risk"] +
        user_reports * WEIGHTS["user_reports"]
    )

    return {
        "safety_score": round(safety_score, 1),
        "breakdown": {
            "lighting": lighting,
            "police_proximity": police_proximity,
            "crime_risk": crime_risk,
            "user_reports": user_reports,
        }
    }


def get_fake_scores_for_point(lat: float, lng: float) -> dict:
    import random
    return {
        "lighting": round(random.uniform(60, 95), 1),
        "police_proximity": round(random.uniform(50, 90), 1),
        "crime_risk": round(random.uniform(55, 90), 1),
        "user_reports": round(random.uniform(70, 100), 1),
    }


def score_route(start: dict, end: dict) -> dict:
    start_scores = get_fake_scores_for_point(start["lat"], start["lng"])
    end_scores = get_fake_scores_for_point(end["lat"], end["lng"])

    avg = {
        key: round((start_scores[key] + end_scores[key]) / 2, 1)
        for key in start_scores
    }

    return calculate_safety_score(**avg)