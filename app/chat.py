"""Persistent AI chat: investigators query case evidence in natural language."""
import json
from . import db
from .llm import generate_text

SYSTEM = """You are CrimeVision AI, a forensic decision-support assistant. Answer ONLY from the
case evidence below. If the evidence does not contain the answer, say so. Cite the source file
and time when possible. You support investigators; you never declare guilt.

CASE EVIDENCE:
{ctx}"""


def ask(case_id: int, question: str) -> str:
    case = db.get_case(case_id)
    ctx = json.dumps({"fused": case["fused"],
                      "evidence": [{"file": e["filename"], "kind": e["kind"], "analysis": e["analysis"]}
                                   for e in case["evidence"]]})[:150000]
    history = [{"role": "user" if m["role"] == "user" else "model", "content": m["content"]}
               for m in db.get_chat(case_id)][-20:]
    answer = generate_text(SYSTEM.format(ctx=ctx), history, question,
                           fallback="[demo] Based on the evidence, a hooded person was seen leaving the scene.")
    db.add_chat(case_id, "user", question)
    db.add_chat(case_id, "assistant", answer)
    return answer
