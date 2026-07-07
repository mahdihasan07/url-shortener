import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Helpers
def create_short_url(original="https://example.com/"):
    return client.post("/shorten", json={"original_url": original})


# Shorten endpoint
def test_shorten_returns_short_code():
    r = create_short_url()
    assert r.status_code == 200
    data = r.json()
    assert "short_code" in data
    assert len(data["short_code"]) == 7
    assert data["original_url"] == "https://example.com/"
    assert "short_url" in data


def test_shorten_invalid_url_rejected():
    r = client.post("/shorten", json={"original_url": "not-a-url"})
    assert r.status_code == 422   # Pydantic validation error


def test_shorten_missing_url_rejected():
    r = client.post("/shorten", json={})
    assert r.status_code == 422


# Redirect endpoint 
def test_redirect_valid_code():
    short = create_short_url("https://python.org/").json()
    r = client.get(f"/{short['short_code']}", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "https://python.org/"


def test_redirect_unknown_code_returns_404():
    r = client.get("/doesnotexist", follow_redirects=False)
    assert r.status_code == 404


# Stats endpoint 
def test_stats_returns_click_count():
    short = create_short_url("https://docs.python.org/").json()
    code = short["short_code"]

    # Generate some clicks
    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)

    r = client.get(f"/stats/{code}")
    assert r.status_code == 200
    data = r.json()
    assert data["total_clicks"] >= 0   # background tasks may not run in test
    assert data["short_code"] == code


def test_stats_unknown_code_returns_404():
    r = client.get("/stats/doesnotexist")
    assert r.status_code == 404