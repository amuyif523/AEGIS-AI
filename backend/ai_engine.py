from .models import IncidentType, IncidentSeverity

class AIEngine:
    def __init__(self):
        # Keywords for Severity (Ordered by priority)
        self.critical_keywords = ["explosion", "bomb", "mass casualty", "terror", "flood", "earthquake", "war", "gunfire", "shooter", "dead", "fatality"]
        self.high_keywords = ["fire", "accident", "crash", "robbery", "riot", "protest", "attack", "burning", "bleeding", "unconscious"]
        self.medium_keywords = ["fight", "injury", "blocked", "traffic", "theft", "break-in", "argument"]
        
        # Keywords for Type
        self.type_map = {
            IncidentType.FIRE: ["fire", "smoke", "flame", "burn", "ash", "esat", "chid"],
            IncidentType.ACCIDENT: ["crash", "collision", "hit", "car", "vehicle", "truck", "bus", "motorcycle", "mekina", "adega"],
            IncidentType.CRIME: ["robbery", "theft", "gun", "knife", "attack", "stolen", "assault", "thief", "leba", "wunjel"],
            IncidentType.MEDICAL: ["injured", "blood", "heart", "breath", "unconscious", "sick", "pain", "ambulance", "hemem", "hospital"],
            IncidentType.UNREST: ["protest", "riot", "crowd", "march", "chanting", "demonstration", "fukera", "gored"],
            IncidentType.HAZARD: ["leak", "wire", "pole", "collapse", "hole", "landslide", "adega"],
            IncidentType.FLOOD: ["flood", "water", "rain", "river", "drowning", "orf"],
            IncidentType.INFRASTRUCTURE: ["power", "electric", "blackout", "water", "pipe", "road", "bridge", "mebrat"],
            IncidentType.CROWD: ["gathering", "festival", "concert", "meeting", "sewb"],
            IncidentType.SUSPICIOUS: ["bomb", "package", "weird", "strange", "terror", "shibir"]
        }

    def analyze(self, text: str) -> dict:
        """
        Analyzes the incident text to determine severity and type.
        Returns a dictionary with 'severity' and 'incident_type'.
        """
        text = text.lower()
        
        result = {
            "severity": IncidentSeverity.LOW, # Default
            "incident_type": IncidentType.OTHER, # Default
            "confidence": 0.5
        }
        
        # 1. Determine Severity (Check Critical -> High -> Medium)
        if any(k in text for k in self.critical_keywords):
            result["severity"] = IncidentSeverity.CRITICAL
        elif any(k in text for k in self.high_keywords):
            result["severity"] = IncidentSeverity.HIGH
        elif any(k in text for k in self.medium_keywords):
            result["severity"] = IncidentSeverity.MEDIUM
            
        # 2. Determine Type
        for type_, keywords in self.type_map.items():
            if any(k in text for k in keywords):
                result["incident_type"] = type_
                break # Take the first match for now
                
        return result

# Singleton instance
ai_engine = AIEngine()
