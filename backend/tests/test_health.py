"""
Health Check Tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"
    assert "services" in data


def test_health_check_services():
    """Test health check services"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    services = data["services"]
    assert "database" in services
    assert "redis" in services
    assert "vector_db" in services

