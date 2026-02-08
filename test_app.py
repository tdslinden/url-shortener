import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_create_url_success(client):
    """Test creating a short URL with valid input"""
    response = client.post("/urls", json={"url": "https://google.com"})

    # Should return 201 (Created), not 200
    assert response.status_code == 201

    assert "short_code" in response.json
    assert "short_url" in response.json

    # Short code should be 6 characters
    assert len(response.json["short_code"]) == 6


def test_create_url_missing_url(client):
    """Test creating a short URL with missing 'url' field"""
    response = client.post("/urls", json={})

    # Should return 400 (Bad Request)
    assert response.status_code == 400

    assert "error" in response.json


def test_redirect_valid_code(client):
    """Test that valid short code redirects to original URL"""
    initial_response = client.post("urls", json={"url": "https://google.com"})
    short_code = initial_response.json["short_code"]

    response = client.get(f"/{short_code}")

    assert response.status_code in [301, 302]
    assert response.location == "https://google.com"


def test_redirect_invalid_code(client):
    """Test that invalid short code returns 404"""
    response = client.get("/INVALID")

    assert response.status_code == 404
    assert "error" in response.json


def test_redirect_incremental_clicks(client):
    """Test that valid short code redirects to original URL"""
    initial_response = client.post("urls", json={"url": "https://google.com"})
    short_code = initial_response.json["short_code"]

    client.get(f"/{short_code}")

    # Check clicks were tracked (we'll build stats endpoint tomorrow)
    # For now, just verify redirect still works after multiple accesses
    response = client.get(f"/{short_code}")
    assert response.status_code in [301, 302]


def test_get_stats_valid_code(client):
    """Test getting stats for a valid short code"""

    initial_response = client.post("urls", json={"url": "https://google.com"})
    short_code = initial_response.json["short_code"]

    client.get(f"/{short_code}")

    response = client.get(f"/urls/{short_code}/stats")

    assert response.status_code == 200
    assert response.json["short_code"] == short_code
    assert response.json["original_url"] == "https://google.com"
    assert response.json["clicks"] == 1
    assert "created_at" in response.json


def test_get_stats_invalid_code(client):
    """Test getting stats for an invalid short code"""

    response = client.get("/urls/INVALID/stats")

    assert response.status_code == 404
    assert "error" in response.json


def test_create_url_format_invalid(client):
    """Test creating a short URL with invalid input"""
    response = client.post("/urls", json={"url": "not a url"})
    assert response.status_code == 400
    assert "error" in response.json

    response = client.post("/urls", json={"url": "google.com"})
    assert response.status_code == 400
    assert "error" in response.json

    response = client.post("/urls", json={"url": ""})
    assert response.status_code == 400
    assert "error" in response.json
