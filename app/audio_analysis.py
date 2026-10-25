"""Epic 3: Audio analysis - witness statement transcription and event extraction."""
import mimetypes
from .llm import generate_json

PROMPT = """You are a forensic audio analyst. Transcribe this witness audio and extract facts. Return JSON:
{"transcript": str,
 "language": str,
 "speakers": [str],
 "events": [{"time_reference": str, "description": str}],
 "people_mentioned": [str],
 "locations_mentioned": [str],
 "emotional_tone": str,
 "background_sounds": [str],
 "reliability_notes": str}
Use "unknown" for time_reference when no time is stated."""

FALLBACK = {
    "transcript": "[demo] I heard a loud bang around 9:40 and saw someone in a dark hoodie run past the garage.",
    "language": "en",
    "speakers": ["Witness 1"],
    "events": [{"time_reference": "21:40", "description": "Loud bang heard"},
               {"time_reference": "21:41", "description": "Person in dark hoodie ran past garage"}],
    "people_mentioned": [],
    "locations_mentioned": ["parking garage"],
    "emotional_tone": "anxious",
    "background_sounds": ["traffic"],
    "reliability_notes": "Witness appears certain about clothing, less certain about time.",
}


def analyze_audio_file(path: str) -> dict:
    mime = mimetypes.guess_type(path)[0] or "audio/mpeg"
    with open(path, "rb") as f:
        return generate_json(PROMPT, [(f.read(), mime)], FALLBACK)
