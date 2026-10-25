"""Thin wrapper around Gemini (Google Cloud Generative AI) with a demo fallback."""
import json
import re
from typing import Optional

from .config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        from google import genai
        if settings.use_vertex:
            _client = genai.Client(vertexai=True, project=settings.gcp_project,
                                   location=settings.gcp_location)
        else:
            _client = genai.Client(api_key=settings.google_api_key)
    return _client


def _parse_json(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(text)


def generate_json(prompt: str, media: Optional[list] = None, fallback: Optional[dict] = None):
    """media: list of (bytes, mime_type). Returns parsed JSON."""
    if settings.demo_mode:
        return fallback or {}
    from google.genai import types
    parts = [types.Part.from_bytes(data=b, mime_type=m) for b, m in (media or [])]
    parts.append(prompt)
    resp = _get_client().models.generate_content(
        model=settings.model_name, contents=parts,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2),
    )
    return _parse_json(resp.text)


def generate_text(system: str, history: list, question: str, fallback: str = "") -> str:
    if settings.demo_mode:
        return fallback
    from google.genai import types
    contents = [types.Content(role=h["role"], parts=[types.Part(text=h["content"])]) for h in history]
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
    resp = _get_client().models.generate_content(
        model=settings.model_name, contents=contents,
        config=types.GenerateContentConfig(system_instruction=system, temperature=0.3),
    )
    return resp.text
