"""
Sentiment Analysis - Intent Triage

A tool that classifies text messages as questions, comments, or complaints.
"""

__version__ = "1.0.0"
__author__ = "Sinbad Adjuik"

from src.modeling.predict import get_classifier, IntentClassifier
from src.models import ClassificationRequest, ClassificationResponse, HealthResponse
from src.config import config

__all__ = [
    'get_classifier',
    'IntentClassifier',
    'ClassificationRequest',
    'ClassificationResponse',
    'HealthResponse',
    'config',
]
