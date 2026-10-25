"""Epic 1: environment configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    google_api_key = os.getenv("GOOGLE_API_KEY", "")
    use_vertex = os.getenv("USE_VERTEX", "false").lower() == "true"
    gcp_project = os.getenv("GCP_PROJECT", "")
    gcp_location = os.getenv("GCP_LOCATION", "us-central1")
    model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    frame_interval = int(os.getenv("FRAME_INTERVAL_SEC", "3"))
    max_frames = int(os.getenv("MAX_FRAMES", "12"))
    db_path = os.getenv("DB_PATH", str(BASE_DIR / "data" / "crimevision.db"))
    upload_dir = BASE_DIR / "data" / "uploads"
    report_dir = BASE_DIR / "data" / "reports"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.report_dir.mkdir(parents=True, exist_ok=True)
