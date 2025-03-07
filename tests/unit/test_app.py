"""Tests for the main application."""

import pytest
from fastapi.testclient import TestClient

from learned_knowledge_mcp.app import app


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


def test_read_main(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Learned Knowledge MCP"


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"