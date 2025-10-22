"""
Unit tests for Pydantic data models.

This module tests the validation and structure of our API data models
to ensure they correctly validate input and maintain data integrity.
"""
import pytest
from src.models import ClassificationRequest, ClassificationResponse


def test_classification_request_valid():
    """Test that a valid classification request is accepted"""
    request = ClassificationRequest(text="How do I reset my password?")
    assert request.text == "How do I reset my password?"


def test_classification_request_empty_fails():
    """Test that empty text is rejected by Pydantic validation"""
    with pytest.raises(ValueError):
        ClassificationRequest(text="")


def test_classification_response_structure():
    """Test that classification response has correct structure and types"""
    response = ClassificationResponse(
        label="question",
        confidence=85.5,
        reason="Contains interrogative words",
        escalate=False
    )
    assert response.label == "question"
    assert response.confidence == 85.5
    assert response.escalate is False


# TODO: Add more comprehensive model validation tests in task 8
