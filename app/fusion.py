"""Epic 5: Multimodal fusion - merge image/audio/video findings into one forensic timeline."""
import json
from .llm import generate_json

PROMPT = """You are a senior forensic analyst. Combine the following multimodal evidence analyses
(images, video frame timelines, witness audio) into ONE unified, chronological forensic report.
Flag contradictions between sources. Do not assert guilt; state confidence. Return JSON:
{"summary": str,
 "timeline": [{"order": int, "time": str, "source": str, "event": str, "confidence": float}],
 "persons_of_interest": [{"description": str, "evidence": [str]}],
 "weapons_and_objects": [str],
 "inconsistencies": [str],
 "recommended_follow_up": [str]}

EVIDENCE:
"""


def _local_merge(evidence):
    """Deterministic fallback so the pipeline works even without an LLM."""
    events = []
    for ev in evidence:
        a, k = ev.get("analysis") or {}, ev["kind"]
        src = f"{k}:{ev['filename']}"
        if k == "video":
            for t in a.get("timeline", []):
                events.append({"time": f"{t['timestamp_sec']}s", "source": src,
                               "event": t["description"], "confidence": 0.7})
        elif k == "audio":
            for e in a.get("events", []):
                events.append({"time": e.get("time_reference", "unknown"), "source": src,
                               "event": e.get("description", ""), "confidence": 0.6})
        elif k == "image":
            events.append({"time": "unknown", "source": src,
                           "event": a.get("scene_description", ""), "confidence": 0.7})
    events.sort(key=lambda e: (e["time"] == "unknown", e["time"]))
    for i, e in enumerate(events, 1):
        e["order"] = i
    return events


def fuse(evidence: list) -> dict:
    slim = [{"kind": e["kind"], "filename": e["filename"], "analysis": e["analysis"]}
            for e in evidence if e.get("analysis")]
    fallback = {"summary": "[demo] Evidence suggests a person in a dark hoodie left the scene shortly after a loud noise.",
                "timeline": _local_merge(evidence), "persons_of_interest": [],
                "weapons_and_objects": [], "inconsistencies": [], "recommended_follow_up": []}
    return generate_json(PROMPT + json.dumps(slim)[:200000], None, fallback)
