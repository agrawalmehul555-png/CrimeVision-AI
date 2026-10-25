"""Epic 2: Image analysis - people, weapons, objects, actions, scene description."""
from .llm import generate_json

PROMPT = """You are a forensic image analyst. Examine this crime-scene image objectively.
Only report what is visibly present; do not speculate about guilt. Return JSON:
{"scene_description": str,
 "people": [{"description": str, "action": str, "confidence": float}],
 "weapons": [{"type": str, "location": str, "confidence": float}],
 "objects": [{"name": str, "location": str, "forensic_relevance": str}],
 "suspicious_activity": [str],
 "lighting_and_conditions": str}"""

FALLBACK = {
    "scene_description": "[demo] Dimly lit parking garage with a parked sedan and scattered items.",
    "people": [{"description": "Person in dark hooded jacket", "action": "running toward exit", "confidence": 0.82}],
    "weapons": [{"type": "possible knife", "location": "ground near vehicle", "confidence": 0.55}],
    "objects": [{"name": "backpack", "location": "beside car", "forensic_relevance": "possible abandoned item"}],
    "suspicious_activity": ["Person leaving scene quickly"],
    "lighting_and_conditions": "Low light, artificial overhead lighting",
}


def analyze_image_bytes(data: bytes, mime: str = "image/jpeg") -> dict:
    return generate_json(PROMPT, [(data, mime)], FALLBACK)


def analyze_image_file(path: str) -> dict:
    mime = "image/png" if str(path).lower().endswith(".png") else "image/jpeg"
    with open(path, "rb") as f:
        return analyze_image_bytes(f.read(), mime)
