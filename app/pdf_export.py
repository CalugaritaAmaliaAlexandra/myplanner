from __future__ import annotations
from datetime import date as Date, timedelta
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from .models import Event

def export_week_pdf(any_date: Date, events: List[Event]) -> bytes:
    monday = any_date - timedelta(days=any_date.weekday())
    sunday = monday + timedelta(days=6)

    import io
    bio = io.BytesIO()
    c = canvas.Canvas(bio, pagesize=A4)

    width, height = A4
    x = 2 * cm
    y = height - 2 * cm

    title = f"Weekly agenda: {monday.strftime('%d.%m.%Y')} – {sunday.strftime('%d.%m.%Y')}"
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, title)

    y -= 1.2 * cm
    c.setFont("Helvetica", 10)

    if not events:
        c.drawString(x, y, "No events for this week.")
        c.showPage()
        c.save()
        return bio.getvalue()

    # Group by date
    from collections import defaultdict
    grouped = defaultdict(list)
    for e in events:
        grouped[e.date].append(e)

    # Sort dates
    dates = sorted(grouped.keys())

    for ds in dates:
        day_events = sorted(grouped[ds], key=lambda e: e.time)
        # Date header
        try:
            d = Date.fromisoformat(ds)
            header = d.strftime("%A, %d.%m.%Y")
        except Exception:
            header = ds

        c.setFont("Helvetica-Bold", 11)
        c.drawString(x, y, header)
        y -= 0.6 * cm

        c.setFont("Helvetica", 10)
        for e in day_events:
            line = f"{e.time}  •  {e.title}  [{e.category}]"
            if y < 2.2 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica", 10)
            c.drawString(x, y, line)
            y -= 0.5 * cm
            if e.description:
                desc = e.description.strip().replace("\n", " ")
                # Wrap to max width
                max_chars = 110
                for i in range(0, len(desc), max_chars):
                    chunk = desc[i:i+max_chars]
                    if y < 2.2 * cm:
                        c.showPage()
                        y = height - 2 * cm
                        c.setFont("Helvetica", 10)
                    c.drawString(x + 0.8*cm, y, f"- {chunk}")
                    y -= 0.45 * cm
        y -= 0.3 * cm

    c.showPage()
    c.save()
    return bio.getvalue()
