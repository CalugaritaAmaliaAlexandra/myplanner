from __future__ import annotations

from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, send_file
from datetime import date as Date, datetime, timedelta
import io

from .models import (
    CATEGORIES,
    create_event,
    get_event,
    update_event,
    delete_event,
    list_events_for_date,
    list_events_for_month,
    search_events,
    list_events_for_week,
)
from .calendar_utils import month_grid, month_name
from .pdf_export import export_week_pdf, export_month_pdf

bp = Blueprint("main", __name__)

def _db():
    return current_app.config["DB_PATH"]

def _parse_int(value, default):
    try:
        return int(value)
    except Exception:
        return default

def _validate_event_form(form) -> tuple[bool, dict, list[str]]:
    errors = []
    title = (form.get("title") or "").strip()
    date_str = (form.get("date") or "").strip()
    time_str = (form.get("time") or "").strip()
    category = (form.get("category") or "").strip()
    description = (form.get("description") or "").strip()

    # Validate title
    if len(title) < 3:
        errors.append("Title must be at least 3 characters.")

    # Validate date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        errors.append("Date must be in YYYY-MM-DD format.")

    # Validate time
    try:
        datetime.strptime(time_str, "%H:%M")
    except Exception:
        errors.append("Time must be in HH:MM format (e.g., 14:30).")

    if category not in CATEGORIES:
        errors.append("Selected category is not valid.")

    data = dict(title=title, date=date_str, time=time_str, category=category, description=description)
    return (len(errors) == 0), data, errors

@bp.get("/")
def home():
    today = Date.today()
    return redirect(url_for("main.calendar_view", year=today.year, month=today.month))

@bp.get("/calendar")
def calendar_view():
    today = Date.today()
    year = _parse_int(request.args.get("year"), today.year)
    month = _parse_int(request.args.get("month"), today.month)

    events = list_events_for_month(_db(), year, month)
    counts = {}
    for e in events:
        counts[e.date] = counts.get(e.date, 0) + 1

    grid = month_grid(year, month, counts)

    # prev/next month
    first = Date(year, month, 1)
    prev_month = (first - timedelta(days=1)).replace(day=1)
    next_month = (first.replace(day=28) + timedelta(days=4)).replace(day=1)

    return render_template(
        "calendar.html",
        year=year,
        month=month,
        month_title=month_name(year, month),
        grid=grid,
        prev_year=prev_month.year,
        prev_month=prev_month.month,
        next_year=next_month.year,
        next_month=next_month.month,
        today=today.isoformat(),
        categories=CATEGORIES,
    )

@bp.get("/day/<date_str>")
def day_view(date_str: str):
    # date_str expected YYYY-MM-DD
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        flash("Invalid date.", "danger")
        return redirect(url_for("main.home"))

    events = list_events_for_date(_db(), date_str)
    return render_template("day.html", date=d, date_str=date_str, events=events)

@bp.route("/add", methods=["GET", "POST"])
def add_event_view():
    if request.method == "POST":
        ok, data, errors = _validate_event_form(request.form)
        if not ok:
            for err in errors:
                flash(err, "danger")
            return render_template("add_event.html", categories=CATEGORIES, form=data)

        eid = create_event(_db(), **data)
        flash("Event added.", "success")
        return redirect(url_for("main.event_details", event_id=eid))

    # defaults
    today = Date.today().isoformat()
    return render_template("add_event.html", categories=CATEGORIES, form={"date": today, "time": "09:00", "category": CATEGORIES[0]})

@bp.get("/event/<int:event_id>")
def event_details(event_id: int):
    event = get_event(_db(), event_id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.home"))
    return render_template("event_details.html", event=event)

@bp.route("/edit/<int:event_id>", methods=["GET", "POST"])
def edit_event_view(event_id: int):
    event = get_event(_db(), event_id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.home"))

    if request.method == "POST":
        ok, data, errors = _validate_event_form(request.form)
        if not ok:
            for err in errors:
                flash(err, "danger")
            return render_template("edit_event.html", categories=CATEGORIES, event_id=event_id, form=data)

        update_event(_db(), event_id, **data)
        flash("Event updated.", "success")
        return redirect(url_for("main.event_details", event_id=event_id))

    return render_template("edit_event.html", categories=CATEGORIES, event_id=event_id, form={
        "title": event.title,
        "date": event.date,
        "time": event.time,
        "category": event.category,
        "description": event.description,
    })

@bp.post("/delete/<int:event_id>")
def delete_event_view(event_id: int):
    ok = delete_event(_db(), event_id)
    if ok:
        flash("Event deleted.", "success")
    else:
        flash("Event not found.", "warning")
    return redirect(url_for("main.home"))

@bp.get("/search")
def search_view():
    q = (request.args.get("q") or "").strip()
    category = (request.args.get("category") or "").strip()
    date_from = (request.args.get("date_from") or "").strip()
    date_to = (request.args.get("date_to") or "").strip()

    # Empty search just shows page
    events = []
    if any([q, category, date_from, date_to]):
        events = search_events(_db(), q=q, category=category, date_from=date_from, date_to=date_to)

    return render_template(
        "search.html",
        q=q,
        category=category,
        date_from=date_from,
        date_to=date_to,
        events=events,
        categories=[""] + CATEGORIES,
    )

@bp.get("/export/week")
def export_week():
    date_str = (request.args.get("date") or "").strip()
    if not date_str:
        date_str = Date.today().isoformat()

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        flash("Invalid date for export.", "danger")
        return redirect(url_for("main.home"))

    events = list_events_for_week(_db(), d)
    pdf_bytes = export_week_pdf(d, events)

    filename = f"agenda_{d.isoformat()}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
@bp.get("/export/month")
def export_month():
    today = Date.today()
    year = _parse_int(request.args.get("year"), today.year)
    month = _parse_int(request.args.get("month"), today.month)

    if month < 1 or month > 12:
        flash("Invalid month.", "danger")
        return redirect(url_for("main.home"))

    events = list_events_for_month(_db(), year, month)
    pdf_bytes = export_month_pdf(year, month, events)

    filename = f"agenda_{year:04d}-{month:02d}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )