# MyPlanner (Calendar & Appointments) — Flask + SQLite

Local web app (runs on your computer) to manage events in a monthly calendar + day view, with full CRUD, search/filtering, and PDF export (weekly agenda).

## Install
```bash
python3 -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt
```

## Run
```bash
python run.py
```
Open in browser: http://127.0.0.1:5000

Database is created automatically at `data/events.db`.

## Features
- Monthly calendar (navigate months)
- Days show event counts
- Day view (events for selected day)
- CRUD: Add / Edit / Delete / Details
- Search by keyword + filter by category + date range
- Weekly agenda PDF export (Mon–Sun)

## Tests
```bash
pytest -q
```
