"""SQLite persistence: cases, evidence, chat history (persistent chat)."""
import json
import sqlite3
from contextlib import contextmanager
from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS cases(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT,
  fused TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER, kind TEXT,
  filename TEXT, path TEXT, analysis TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS chat(id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER, role TEXT,
  content TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""


@contextmanager
def conn():
    c = sqlite3.connect(settings.db_path)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    try:
        yield c
        c.commit()
    finally:
        c.close()


def create_case(title, description=""):
    with conn() as c:
        return c.execute("INSERT INTO cases(title,description) VALUES(?,?)", (title, description)).lastrowid


def get_case(case_id):
    with conn() as c:
        r = c.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        if not r:
            return None
        d = dict(r)
        d["fused"] = json.loads(d["fused"]) if d["fused"] else None
        ev = c.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY id", (case_id,)).fetchall()
        d["evidence"] = [{**dict(e), "analysis": json.loads(e["analysis"]) if e["analysis"] else None} for e in ev]
        return d


def list_cases():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT id,title,description,created_at FROM cases ORDER BY id DESC")]


def add_evidence(case_id, kind, filename, path):
    with conn() as c:
        return c.execute("INSERT INTO evidence(case_id,kind,filename,path) VALUES(?,?,?,?)",
                         (case_id, kind, filename, str(path))).lastrowid


def save_analysis(evidence_id, analysis):
    with conn() as c:
        c.execute("UPDATE evidence SET analysis=? WHERE id=?", (json.dumps(analysis), evidence_id))


def save_fused(case_id, fused):
    with conn() as c:
        c.execute("UPDATE cases SET fused=? WHERE id=?", (json.dumps(fused), case_id))


def add_chat(case_id, role, content):
    with conn() as c:
        c.execute("INSERT INTO chat(case_id,role,content) VALUES(?,?,?)", (case_id, role, content))


def get_chat(case_id):
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT role,content,created_at FROM chat WHERE case_id=? ORDER BY id", (case_id,))]
