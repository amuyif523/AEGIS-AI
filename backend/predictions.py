from typing import List, Dict
from . import models

# Simple heuristic overlays for academic/demo use
CRIME_HOTSPOTS = [
    {"lat": 9.01, "lng": 38.75, "score": 0.7, "label": "Crime hotspot A"},
    {"lat": 9.03, "lng": 38.76, "score": 0.5, "label": "Crime hotspot B"},
]

FIRE_RISK_ZONES = [
    {"bbox": [38.74, 8.99, 38.79, 9.04], "score": 0.6, "label": "Fire Risk Zone 1"},
]

FLOOD_RISK_ZONES = [
    {"bbox": [38.73, 8.97, 38.80, 9.05], "score": 0.65, "label": "Flood Risk Zone A"},
]

UNREST_PATTERN = [
    {"lat": 9.02, "lng": 38.74, "score": 0.55, "label": "Unrest cluster"},
]

CROWD_ESTIMATE = [
    {"lat": 9.015, "lng": 38.755, "count": 120, "label": "Crowd estimate"},
]


def forecast() -> Dict[str, List[dict]]:
    return {
        "crime_hotspots": CRIME_HOTSPOTS,
        "fire_risk": FIRE_RISK_ZONES,
        "flood_risk": FLOOD_RISK_ZONES,
        "unrest": UNREST_PATTERN,
        "crowd_density": CROWD_ESTIMATE,
    }
