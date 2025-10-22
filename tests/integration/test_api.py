"""
Integration tests for API endpoints.

These tests verify that our API endpoints work correctly end-to-end,
including request validation, response formatting, and error handling.
"""
import pytest
from fastapi.testclient import TestClient
from src.services.api import app

# Create a test client for making API requests
client = TestClient(app)


def test_health_endpoint():
    """
    Test the health check endpoint returns correct status information.
    
    Verifies that the service is running and provides version/availability info.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "ai_model_available" in data


def test_root_endpoint():
    """
    Test the root endpoint is accessible.
    
    Verifies basic connectivity to the API.
    """
    response = client.get("/")
    assert response.status_code == 200


def test_classify_endpoint_valid_request():
    """
    Test the classification endpoint with valid input.
    
    Verifies that a proper request returns all required fields
    with correct types and valid values.
    """
    response = client.post(
        "/classify",
        json={"text": "How do I reset my password?"}
    )
    assert response.status_code == 200
    data = response.json()
    # Check all required response fields are present
    assert "label" in data
    assert "confidence" in data
    assert "reason" in data
    assert "escalate" in data
    # Verify label is one of the valid options
    assert data["label"] in ["question", "comment", "complaint"]


def test_classify_endpoint_empty_text():
    """
    Test that the classification endpoint rejects empty text.
    
    Should return 422 Unprocessable Entity due to validation failure.
    """
    response = client.post(
        "/classify",
        json={"text": ""}
    )
    assert response.status_code == 422  # Validation error


# TODO: Add more comprehensive integration tests in task 8
# - Test different message types (questions, comments, complaints)
# - Test edge cases (very long text, special characters, etc.)
# - Test error handling scenarios
