"""Epic 6: REST API (FastAPI)."""
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import chat, db, fusion
from .audio_analysis import analyze_audio_file
from .config import settings
from .image_analysis import analyze_image_file
from .report import build_report
from .video_analysis import analyze_video_file

app = FastAPI(title="CrimeVision AI", version="1.0.0")

KINDS = {".jpg": "image", ".jpeg": "image", ".png": "image", ".webp": "image",
         ".mp4": "video", ".avi": "video", ".mov": "video", ".mkv": "video",
         ".mp3": "audio", ".wav": "audio", ".m4a": "audio", ".ogg": "audio", ".flac": "audio"}
ANALYZERS = {"image": analyze_image_file, "audio": analyze_audio_file, "video": analyze_video_file}


class CaseIn(BaseModel):
    title: str
    description: str = ""


class ChatIn(BaseModel):
    question: str


def _case_or_404(case_id):
    c = db.get_case(case_id)
    if not c:
        raise HTTPException(404, "Case not found")
    return c


@app.get("/health")
def health():
    return {"status": "ok", "demo_mode": settings.demo_mode, "model": settings.model_name}


@app.post("/cases")
def new_case(body: CaseIn):
    return {"id": db.create_case(body.title, body.description)}


@app.get("/cases")
def cases():
    return db.list_cases()


@app.get("/cases/{case_id}")
def case(case_id: int):
    return _case_or_404(case_id)


@app.post("/cases/{case_id}/evidence")
async def upload(case_id: int, file: UploadFile = File(...)):
    _case_or_404(case_id)
    ext = Path(file.filename).suffix.lower()
    if ext not in KINDS:
        raise HTTPException(400, f"Unsupported file type {ext}")
    dest = settings.upload_dir / f"{uuid.uuid4().hex}{ext}"
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    eid = db.add_evidence(case_id, KINDS[ext], file.filename, dest)
    return {"evidence_id": eid, "kind": KINDS[ext]}


@app.post("/cases/{case_id}/analyze")
def analyze(case_id: int):
    c = _case_or_404(case_id)
    if not c["evidence"]:
        raise HTTPException(400, "No evidence uploaded")
    for ev in c["evidence"]:
        if not ev["analysis"]:
            try:
                db.save_analysis(ev["id"], ANALYZERS[ev["kind"]](ev["path"]))
            except Exception as e:  # keep going; record which file failed
                db.save_analysis(ev["id"], {"error": str(e)})
    c = db.get_case(case_id)
    fused = fusion.fuse(c["evidence"])
    db.save_fused(case_id, fused)
    return fused


@app.post("/cases/{case_id}/chat")
def ask(case_id: int, body: ChatIn):
    c = _case_or_404(case_id)
    if not c["fused"]:
        raise HTTPException(400, "Analyze the case before chatting")
    return {"answer": chat.ask(case_id, body.question)}


@app.get("/cases/{case_id}/chat")
def history(case_id: int):
    _case_or_404(case_id)
    return db.get_chat(case_id)


@app.get("/cases/{case_id}/report")
def report(case_id: int):
    path = build_report(_case_or_404(case_id))
    return FileResponse(path, media_type="application/pdf", filename=Path(path).name)
