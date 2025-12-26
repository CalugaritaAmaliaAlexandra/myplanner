import os
import tempfile
import pytest
from app import create_app

@pytest.fixture()
def client():
    with tempfile.TemporaryDirectory() as td:
        app = create_app()
        app.config["TESTING"] = True
        app.config["DB_PATH"] = os.path.join(td, "events.db")

        # re-init db at new path
        from app.models import init_db
        init_db(app.config["DB_PATH"])

        with app.test_client() as c:
            yield c

def test_home_redirect(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (301, 302)

def test_add_event_flow(client):
    # GET add
    r = client.get("/add")
    assert r.status_code == 200

    # POST add
    r2 = client.post("/add", data={
        "title": "Eveniment",
        "date": "2025-12-26",
        "time": "09:30",
        "category": "personal",
        "description": "abc",
    }, follow_redirects=False)
    assert r2.status_code in (301, 302)

    # Calendar page
    r3 = client.get("/calendar?year=2025&month=12")
    assert r3.status_code == 200
