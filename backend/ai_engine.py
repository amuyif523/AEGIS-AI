from .models import IncidentType, IncidentSeverity


class AIEngine:
    def __init__(self):
        # Keywords for Severity (Ordered by priority) includes Amharic terms
        self.critical_keywords = ["explosion", "bomb", "mass casualty", "terror", "flood", "earthquake", "war", "gunfire", "shooter", "dead", "fatality", "bomb", "ሙቀት", "ጦር"]
        self.high_keywords = ["fire", "accident", "crash", "robbery", "riot", "protest", "attack", "burning", "bleeding", "unconscious", "ፍንዳታ", "ድርቅ", "እሳት", "ግጭት"]
        self.medium_keywords = ["fight", "injury", "blocked", "traffic", "theft", "break-in", "argument", "ትራፊክ", "መከላከያ"]
        
        # Keywords for Type
        self.type_map = {
            IncidentType.FIRE: ["fire", "smoke", "flame", "burn", "ash", "esat", "chid", "እሳት", "ጭስ", "ቃጠሎ"],
            IncidentType.ACCIDENT: ["crash", "collision", "hit", "car", "vehicle", "truck", "bus", "motorcycle", "mekina", "adega", "አደጋ", "መኪና"],
            IncidentType.CRIME: ["robbery", "theft", "gun", "knife", "attack", "stolen", "assault", "thief", "leba", "wunjel", "ስርቆት", "ግድያ"],
            IncidentType.MEDICAL: ["injured", "blood", "heart", "breath", "unconscious", "sick", "pain", "ambulance", "hemem", "hospital", "ህመም", "አስቸኳይ", "ደም"],
            IncidentType.UNREST: ["protest", "riot", "crowd", "march", "chanting", "demonstration", "fukera", "gored", "ሰልፍ", "ተቃውሞ"],
            IncidentType.HAZARD: ["leak", "wire", "pole", "collapse", "hole", "landslide", "adega", "ስርየት", "መፍሰስ"],
            IncidentType.FLOOD: ["flood", "water", "rain", "river", "drowning", "orf", "ጎርፍ", "ዝናብ", "ውሃ"],
            IncidentType.INFRASTRUCTURE: ["power", "electric", "blackout", "water", "pipe", "road", "bridge", "mebrat", "እልባት", "መንገድ"],
            IncidentType.CROWD: ["gathering", "festival", "concert", "meeting", "sewb", "ብዛት", "ሕዝብ"],
            IncidentType.SUSPICIOUS: ["bomb", "package", "weird", "strange", "terror", "shibir", "እገርጋሪ", "ጥርጣሬ"],
            IncidentType.PUBLIC_DISTURBANCE if hasattr(IncidentType, "PUBLIC_DISTURBANCE") else IncidentType.OTHER: ["noise", "disturbance", "loud", "ውይይት"],
        }

    def analyze(self, text: str) -> dict:
        """
        Analyzes the incident text to determine severity and type.
        Returns a dictionary with severity/type plus confidence and risk cues.
        """
        text = text.lower()
        
        result = {
            "severity": IncidentSeverity.LOW,  # Default
            "incident_type": IncidentType.OTHER,  # Default
            "confidence": 0.3,
            "escalation_probability": 0.1,
            "spread_risk": 0.1,
            "casualty_likelihood": 0.1,
            "crowd_size_estimate": 0
        }
        
        # 1. Determine Severity
        if any(k in text for k in self.critical_keywords):
            result["severity"] = IncidentSeverity.CRITICAL
            result["confidence"] = 0.85
        elif any(k in text for k in self.high_keywords):
            result["severity"] = IncidentSeverity.HIGH
            result["confidence"] = 0.7
        elif any(k in text for k in self.medium_keywords):
            result["severity"] = IncidentSeverity.MEDIUM
            result["confidence"] = 0.5
        
        # 2. Determine Type
        for type_, keywords in self.type_map.items():
            if any(k in text for k in keywords):
                result["incident_type"] = type_
                result["confidence"] = max(result["confidence"], 0.6)
                break

        # 3. Simple risk heuristics
        if result["incident_type"] in [IncidentType.FIRE, IncidentType.FLOOD, IncidentType.UNREST]:
            result["escalation_probability"] = 0.6 if result["severity"] in [IncidentSeverity.MEDIUM, IncidentSeverity.HIGH] else 0.8
            result["spread_risk"] = 0.7 if result["severity"] in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL] else 0.4
        if result["incident_type"] in [IncidentType.MEDICAL, IncidentType.CRIME, IncidentType.ACCIDENT]:
            result["casualty_likelihood"] = 0.6 if result["severity"] in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL] else 0.3
        if result["incident_type"] in [IncidentType.CROWD, IncidentType.UNREST]:
            result["crowd_size_estimate"] = 50 if result["severity"] in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL] else 20
        if result["severity"] == IncidentSeverity.CRITICAL:
            result["escalation_probability"] = max(result["escalation_probability"], 0.85)
            result["spread_risk"] = max(result["spread_risk"], 0.8)
            result["casualty_likelihood"] = max(result["casualty_likelihood"], 0.7)

        return result


# Singleton instance
ai_engine = AIEngine()
