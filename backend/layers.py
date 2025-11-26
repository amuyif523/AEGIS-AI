"""
Static base layers for GIS overlays (stub data for MVP).
"""

BASE_LAYERS = {
    "admin_boundaries": [
        {"name": "Addis Central", "bbox": [38.74, 8.95, 38.82, 9.05]},
    ],
    "police_districts": [
        {"name": "PD-1", "bbox": [38.75, 8.97, 38.80, 9.02]},
    ],
    "fire_districts": [
        {"name": "FD-1", "bbox": [38.76, 8.98, 38.81, 9.03]},
    ],
    "hospitals": [
        {"name": "Black Lion Hospital", "lat": 9.020, "lng": 38.746},
    ],
    "hydrants": [
        {"lat": 9.015, "lng": 38.750},
        {"lat": 9.025, "lng": 38.760},
    ],
    "critical_infra": [
        {"name": "Power Substation", "lat": 9.018, "lng": 38.755},
    ],
    "road_network": [
        {"name": "Ring Road Segment", "coords": [[38.74, 8.98], [38.78, 9.00]]},
    ],
    "water_flood_zones": [
        {"name": "Flood Zone A", "bbox": [38.74, 8.99, 38.79, 9.04]},
    ],
    "weather_overlay": [
        {"type": "rain_cell", "center": [9.01, 38.75], "radius_km": 2},
    ],
}
