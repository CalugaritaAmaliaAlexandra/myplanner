import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
from datetime import date as Date, datetime, timedelta

CATEGORIES = ["school", "personal", "medical", "work", "other"]

@dataclass
class Event:
    id: int
    title: str
    date: str   # YYYY-MM-DD
    time: str   # HH:MM
    category: str
    description: str

def get_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str):
    conn = get_conn(db_path)
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT DEFAULT ''
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);")
        conn.commit()
    finally:
        conn.close()

def create_event(db_path: str, title: str, date: str, time: str, category: str, description: str = "") -> int:
    conn = get_conn(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO events(title, date, time, category, description) VALUES(?,?,?,?,?)",
            (title, date, time, category, description or "")
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()

def get_event(db_path: str, event_id: int) -> Optional[Event]:
    conn = get_conn(db_path)
    try:
        row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        if not row:
            return None
        return Event(**dict(row))
    finally:
        conn.close()

def update_event(db_path: str, event_id: int, title: str, date: str, time: str, category: str, description: str = "") -> bool:
    conn = get_conn(db_path)
    try:
        cur = conn.execute(
            "UPDATE events SET title=?, date=?, time=?, category=?, description=? WHERE id=?",
            (title, date, time, category, description or "", event_id)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def delete_event(db_path: str, event_id: int) -> bool:
    conn = get_conn(db_path)
    try:
        cur = conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def list_events_for_date(db_path: str, date_str: str) -> List[Event]:
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM events WHERE date = ? ORDER BY time ASC",
            (date_str,)
        ).fetchall()
        return [Event(**dict(r)) for r in rows]
    finally:
        conn.close()

def list_events_for_month(db_path: str, year: int, month: int) -> List[Event]:
    # month bounds: YYYY-MM-01 .. next month 01
    start = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end = f"{year+1:04d}-01-01"
    else:
        end = f"{year:04d}-{month+1:02d}-01"
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM events WHERE date >= ? AND date < ? ORDER BY date ASC, time ASC",
            (start, end)
        ).fetchall()
        return [Event(**dict(r)) for r in rows]
    finally:
        conn.close()

def search_events(
    db_path: str,
    q: str = "",
    category: str = "",
    date_from: str = "",
    date_to: str = ""
) -> List[Event]:
    clauses = []
    params: List[Any] = []

    if q:
        clauses.append("(title LIKE ? OR description LIKE ?)")
        like = f"%{q}%"
        params.extend([like, like])

    if category:
        clauses.append("category = ?")
        params.append(category)

    if date_from:
        clauses.append("date >= ?")
        params.append(date_from)

    if date_to:
        clauses.append("date <= ?")
        params.append(date_to)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = f"SELECT * FROM events {where} ORDER BY date ASC, time ASC"

    conn = get_conn(db_path)
    try:
        rows = conn.execute(sql, params).fetchall()
        return [Event(**dict(r)) for r in rows]
    finally:
        conn.close()

def list_events_for_week(db_path: str, any_date: Date) -> List[Event]:
    # Monday..Sunday (inclusive)
    monday = any_date - timedelta(days=any_date.weekday())
    sunday = monday + timedelta(days=6)
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM events WHERE date >= ? AND date <= ? ORDER BY date ASC, time ASC",
            (monday.isoformat(), sunday.isoformat())
        ).fetchall()
        return [Event(**dict(r)) for r in rows]
    finally:
        conn.close()

