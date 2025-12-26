import os
import tempfile
from app.models import init_db, create_event, get_event, update_event, delete_event, search_events

def test_crud_and_search():
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "events.db")
        init_db(db)

        eid = create_event(db, title="Test", date="2025-12-26", time="10:00", category="personal", description="desc")
        e = get_event(db, eid)
        assert e is not None
        assert e.title == "Test"

        ok = update_event(db, eid, title="Test2", date="2025-12-27", time="11:00", category="personal", description="x")
        assert ok
        e2 = get_event(db, eid)
        assert e2.title == "Test2"

        results = search_events(db, q="Test2")
        assert len(results) == 1

        ok_del = delete_event(db, eid)
        assert ok_del
        assert get_event(db, eid) is None
