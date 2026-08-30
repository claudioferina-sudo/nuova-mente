"""Scheda PDF per il registro del docente."""
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from scoring import credits_for, level_label

CREAM = colors.HexColor("#FDF3D0")
GOLD = colors.HexColor("#D4A72C")
INK = colors.HexColor("#2B2620")


def build_report(session: dict, missions_meta: list) -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontName="Times-Bold", textColor=INK, fontSize=20)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Times-Bold", textColor=INK, fontSize=12)
    body = ParagraphStyle("b", parent=ss["BodyText"], fontName="Times-Roman", textColor=INK, fontSize=10, leading=14)

    total = int(session.get("total_points") or 0)
    credits, hours, note = credits_for(total)
    story = [
        Paragraph("DOSSIER 1939 &mdash; SCHEDA DI VALUTAZIONE", h1),
        Paragraph("Nuova-Mente &middot; Escape room didattica &middot; Seconda Guerra Mondiale", body),
        Spacer(1, 8 * mm),
    ]

    info = [
        ["Studente", session.get("student_name", "-"), "Classe", session.get("class_code", "-")],
        ["Avvio", (session.get("started_at") or "-")[:19].replace("T", " "), "Chiusura", (session.get("finished_at") or "in corso")[:19].replace("T", " ")],
        ["Punteggio finale", f"{total}/100", "Crediti autonomia", str(credits)],
        ["Ore PBL sbloccate", f"{hours} h", "Bonus assegnati", str(session.get("bonuses", 0))],
    ]
    t = Table(info, colWidths=[35 * mm, 55 * mm, 35 * mm, 45 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), CREAM),
        ("BACKGROUND", (2, 0), (2, -1), CREAM),
        ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [t, Spacer(1, 8 * mm), Paragraph("DETTAGLIO PER MISSIONE", h2), Spacer(1, 3 * mm)]

    rows = [["#", "Missione", "Punti", "Livello", "Tent.", "Hint", "Stato"]]
    ms = session.get("missions") or {}
    for meta in missions_meta:
        num = str(meta["mission_num"])
        m = ms.get(num) or ms.get(int(num)) or {}
        rows.append([
            num,
            meta["title"][:38],
            f"{m.get('points', 0)}/20",
            level_label(int(m.get("level") or 10)) if m.get("level") else "-",
            str(m.get("attempts", 0)),
            str(m.get("hints_used", 0)),
            "Override docente" if m.get("status") == "overridden" else ("Superata" if m.get("passed") else ("Sbloccata" if m.get("completed") else "Aperta")),
        ])
    mt = Table(rows, colWidths=[10 * mm, 62 * mm, 18 * mm, 24 * mm, 14 * mm, 14 * mm, 28 * mm])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GOLD),
        ("GRID", (0, 0), (-1, -1), 0.4, GOLD),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [mt, Spacer(1, 6 * mm), Paragraph(f"<b>Esito crediti:</b> {note}", body)]

    overrides = session.get("override_log") or []
    if overrides:
        story += [Spacer(1, 6 * mm), Paragraph("OVERRIDE DEL DOCENTE", h2)]
        for o in overrides:
            story.append(Paragraph(
                f"Missione {o.get('mission_num')}: {o.get('old_points')} &rarr; {o.get('new_points')} pt &mdash; {o.get('reason', '')} ({(o.get('at') or '')[:19].replace('T', ' ')})",
                body))

    story += [Spacer(1, 10 * mm), Paragraph("Firma del docente ______________________________", body),
              Spacer(1, 4 * mm), Paragraph("Made with love by Nuova-Mente", body)]
    doc.build(story)
    buf.seek(0)
    return buf
