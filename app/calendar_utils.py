import calendar
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class DayCell:
    day: int           # 0 if padding
    iso_date: str      # '' if padding
    event_count: int

def month_grid(year: int, month: int, event_counts_by_date: Dict[str, int]) -> List[List[DayCell]]:
    cal = calendar.Calendar(firstweekday=0) # Monday first
    weeks = []
    for week in cal.monthdayscalendar(year, month):
        row = []
        for d in week:
            if d == 0:
                row.append(DayCell(day=0, iso_date="", event_count=0))
            else:
                iso = f"{year:04d}-{month:02d}-{d:02d}"
                row.append(DayCell(day=d, iso_date=iso, event_count=event_counts_by_date.get(iso, 0)))
        weeks.append(row)
    return weeks

def month_name(year: int, month: int) -> str:
    return f"{calendar.month_name[month]} {year}"

