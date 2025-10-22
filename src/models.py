"""
Data models for the sentiment analysis service.

This module defines all Pydantic models used for request/response validation
and serialization in the API. Pydantic ensures type safety and automatic
validation of incoming and outgoing data.
"""
from pydantic import BaseModel, Field
from typing import Literal


class ClassificationRequest(BaseModel):
    """
    Request model for text classification endpoint.
    
    Attributes:
        text: The message text to classify. Must be non-empty.
    """
    text: str = Field(
        min_length=1, 
        description="Text to classify",
        examples=["How do I reset my password?"]
    )


class ClassificationResponse(BaseModel):
    """
    Response model for text classification endpoint.
    
    Returns the classification result with confidence metrics and reasoning.
    
    Attributes:
        label: The classified intent (question, comment, or complaint)
        confidence: How confident the model is in its prediction (0-100%)
        reason: A brief human-readable explanation for the classification
        escalate: True if confidence is below threshold and needs human review
    """
    label: Literal["question", "comment", "complaint"] = Field(
        description="Classification label",
        examples=["question"]
    )
    confidence: float = Field(
        ge=0, 
        le=100, 
        description="Confidence score (0-100%)",
        examples=[85.5]
    )
    reason: str = Field(
        description="Short explanation for the classification",
        examples=["Contains interrogative words and seeks information"]
    )
    escalate: bool = Field(
        description="Flag indicating if human review is needed",
        examples=[False]
    )


class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    
    Provides system status and availability information.
    
    Attributes:
        status: Overall health status of the service
        version: Current version of the application
        ai_model_available: Whether AI model is configured and available
    """
    status: str
    version: str
    ai_model_available: bool
