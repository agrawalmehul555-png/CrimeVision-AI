# CrimeVision AI - Intelligent Multimodal Forensic Analysis

Forensic decision-support platform that fuses **image, video and audio** evidence into a unified,
chronological timeline, lets investigators **chat with the evidence**, and exports a **PDF report**.
Built on Gemini (Google Cloud Generative AI), FastAPI and Streamlit.

## Epic -> code map
| Epic | Where |
|---|---|
| 1. Project initialization & environment configuration | `requirements.txt`, `.env.example`, `app/config.py`, `app/db.py`, `Dockerfile` |
| 2. Image analysis (people, weapons, objects, actions, scene) | `app/image_analysis.py` |
| 3. Audio analysis (witness transcripts, events) | `app/audio_analysis.py` |
| 4. Video analysis & timeline generation | `app/video_analysis.py` |
| 5. Multimodal fusion & intelligence generation | `app/fusion.py`, `app/chat.py` |
| 6. Interface, testing, deployment | `app/main.py`, `dashboard.py`, `app/report.py`, `tests/`, `Dockerfile` |

## Architecture
```
Streamlit dashboard --REST--> FastAPI --> image / audio / video analyzers --> Gemini
                                   |--> fusion (unified timeline) --> chat (persistent, SQLite)
                                   '--> report (ReportLab PDF)
```

## Setup (Python 3.9+, per the project's system requirements)
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # add GOOGLE_API_KEY, or set USE_VERTEX=true + GCP_PROJECT
```
Vertex AI option: `gcloud auth application-default login`.

## Run
```bash
uvicorn app.main:app --reload            # API  -> http://localhost:8000/docs
streamlit run dashboard.py               # UI   -> http://localhost:8501
```
No credentials yet? Set `DEMO_MODE=true` in `.env` to run the whole flow with canned AI output.

## Test
```bash
pytest -q
```

## Docker
```bash
docker build -t crimevision-ai . && docker run -p 8000:8000 -p 8501:8501 --env-file .env crimevision-ai
```
Deploy the same image to Google Cloud Run (set the port to 8501 for the UI, or split API/UI into two services).

## API
`POST /cases` - `POST /cases/{id}/evidence` - `POST /cases/{id}/analyze` -
`POST|GET /cases/{id}/chat` - `GET /cases/{id}/report`

## Responsible-use note
Outputs are AI-generated decision support, not proof of guilt. All findings need review by
qualified forensic personnel, and evidence handling must follow your jurisdiction's rules.
