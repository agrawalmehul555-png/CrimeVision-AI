"""Reporting engine: professional forensic PDF."""
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .config import settings


def build_report(case: dict) -> str:
    out = settings.report_dir / f"case_{case['id']}_report.pdf"
    ss = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    p = lambda t, s="BodyText": Paragraph(escape(str(t)), ss[s])
    fused = case.get("fused") or {}
    el = [p("CrimeVision AI - Forensic Analysis Report", "Title"),
          p(f"Case #{case['id']}: {case['title']}", "Heading2"),
          p(f"Generated: {datetime.now():%Y-%m-%d %H:%M}"), Spacer(1, 12),
          p("Case description", "Heading3"), p(case.get("description") or "-"),
          p("Executive summary", "Heading3"), p(fused.get("summary", "Run analysis first."))]

    el += [Spacer(1, 10), p("Evidence reviewed", "Heading3")]
    for e in case["evidence"]:
        el.append(p(f"- [{e['kind']}] {e['filename']}"))

    tl = fused.get("timeline", [])
    if tl:
        el += [Spacer(1, 10), p("Chronological timeline", "Heading3")]
        rows = [["#", "Time", "Source", "Event", "Conf."]]
        for t in tl:
            rows.append([t.get("order", ""), t.get("time", ""),
                         Paragraph(escape(str(t.get("source", ""))), ss["BodyText"]),
                         Paragraph(escape(str(t.get("event", ""))), ss["BodyText"]),
                         f"{float(t.get('confidence', 0)):.0%}"])
        tbl = Table(rows, colWidths=[1*cm, 2*cm, 4*cm, 8*cm, 1.5*cm], repeatRows=1)
        tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4fd8")),
                                 ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                 ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                                 ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        el.append(tbl)

    for title, key in [("Persons of interest", "persons_of_interest"), ("Weapons and objects", "weapons_and_objects"),
                       ("Inconsistencies", "inconsistencies"), ("Recommended follow-up", "recommended_follow_up")]:
        items = fused.get(key, [])
        if items:
            el += [Spacer(1, 10), p(title, "Heading3")]
            el += [p(f"- {i if not isinstance(i, dict) else i.get('description', i)}") for i in items]

    el += [Spacer(1, 20), p("Disclaimer: AI-generated decision-support output. Findings require review "
                            "by qualified forensic personnel and are not proof of guilt.", "Italic")]
    doc.build(el)
    return str(out)
