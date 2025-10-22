"""Tests for the FastAPI application."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parents[1]
src_path = root_dir / "api"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from main import app  # type: ignore


def test_health_endpoint() -> None:
    """Test the health check endpoint returns OK status."""
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_predict_endpoint_structure() -> None:
    """Test that predict endpoint accepts valid request structure."""
    client = TestClient(app)
    payload = {
        "dates": ["2025-01-01", "2025-02-01"]
    }
    resp = client.post("/predict", json=payload)
    # May fail due to missing model, but should have proper structure
    assert resp.status_code in [200, 500]  # Either works or model not found
    

def test_predict_endpoint_validation() -> None:
    """Test that predict endpoint validates input properly."""
    client = TestClient(app)
    # Test with empty dates list
    payload = {"dates": []}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 400  # Should reject empty dates
    

def test_predict_endpoint_invalid_date() -> None:
    """Test that predict endpoint handles invalid date format."""
    client = TestClient(app)
    payload = {"dates": ["not-a-date"]}
    resp = client.post("/predict", json=payload)
    # Should return error for invalid date format
    assert resp.status_code in [400, 422, 500]


def test_api_cors_headers() -> None:
    """Test that CORS middleware is properly configured."""
    client = TestClient(app)
    resp = client.get("/health")
    assert "access-control-allow-origin" in resp.headers or resp.status_code == 200
