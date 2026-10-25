"""Epic 4: Video analysis - sample frames, analyse each, build a per-video timeline."""
import cv2
from .config import settings
from .image_analysis import analyze_image_bytes


def extract_frames(path: str, interval: int = None, max_frames: int = None):
    interval = interval or settings.frame_interval
    max_frames = max_frames or settings.max_frames
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(int(fps * interval), 1)
    frames, idx = [], 0
    while idx < max(total, 1) and len(frames) < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            break
        ok, buf = cv2.imencode(".jpg", frame)
        if ok:
            frames.append((round(idx / fps, 1), buf.tobytes()))
        idx += step
    cap.release()
    return frames


def analyze_video_file(path: str) -> dict:
    frames = extract_frames(path)
    timeline = []
    for ts, data in frames:
        a = analyze_image_bytes(data)
        timeline.append({
            "timestamp_sec": ts,
            "description": a.get("scene_description", ""),
            "people": a.get("people", []),
            "weapons": a.get("weapons", []),
            "suspicious_activity": a.get("suspicious_activity", []),
        })
    return {"frames_analyzed": len(frames), "frame_interval_sec": settings.frame_interval,
            "timeline": timeline}
