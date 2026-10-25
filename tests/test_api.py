import os
os.environ["DEMO_MODE"] = "true"
os.environ["DB_PATH"] = "/tmp/cv_test.db"
if os.path.exists("/tmp/cv_test.db"):
    os.remove("/tmp/cv_test.db")

import cv2
import numpy as np
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _png():
    ok, buf = cv2.imencode(".png", np.zeros((64, 64, 3), dtype=np.uint8))
    return buf.tobytes()


def test_full_pipeline():
    cid = client.post("/cases", json={"title": "Garage incident"}).json()["id"]
    client.post(f"/cases/{cid}/evidence", files={"file": ("scene.png", _png())})
    client.post(f"/cases/{cid}/evidence", files={"file": ("witness.wav", b"RIFF....")})
    fused = client.post(f"/cases/{cid}/analyze").json()
    assert fused["timeline"]
    assert "answer" in client.post(f"/cases/{cid}/chat", json={"question": "Who fled?"}).json()
    assert len(client.get(f"/cases/{cid}/chat").json()) == 2
    r = client.get(f"/cases/{cid}/report")
    assert r.status_code == 200 and r.content[:4] == b"%PDF"


def test_rejects_bad_file():
    cid = client.post("/cases", json={"title": "x"}).json()["id"]
    assert client.post(f"/cases/{cid}/evidence", files={"file": ("a.exe", b"x")}).status_code == 400
