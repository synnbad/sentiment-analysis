"""
Intent classification engine for categorizing text messages.

This module provides both AI-powered and rule-based classification approaches
to determine if a message is a question, comment, or complaint.
"""
import re
import logging
from typing import Tuple, Dict
from src.config import config

# Configure logging
logger = logging.getLogger(__name__)


class RuleBasedClassifier:
    """
    Rule-based classifier using pattern matching and keyword detection.
    
    This serves as a fallback when AI models are unavailable and provides
    a baseline level of functionality using linguistic patterns.
    """
    
    # Question indicators
    QUESTION_WORDS = [
        'what', 'when', 'where', 'who', 'whom', 'whose', 'which', 'why', 'how',
        'can', 'could', 'would', 'should', 'will', 'do', 'does', 'did', 'is', 'are',
        'was', 'were', 'have', 'has', 'had', 'may', 'might', 'must'
    ]
    
    # Complaint indicators
    COMPLAINT_WORDS = [
        'terrible', 'awful', 'horrible', 'worst', 'bad', 'broken', 'useless',
        'disappointed', 'disappointing', 'frustrating', 'frustrated', 'angry',
        'upset', 'unacceptable', 'poor', 'failed', 'failure', 'never works',
        'doesn\'t work', 'not working', 'issue', 'problem', 'bug', 'error',
        'hate', 'ridiculous', 'pathetic', 'disgusted', 'waste', 'wrong',
        'crash', 'crashing', 'waiting', 'hours', 'refund', 'unhappy', 'quality',
        'worse', 'service', 'support', 'fix', 'constantly', 'stop'
    ]
    
    # Positive comment indicators
    POSITIVE_WORDS = [
        'great', 'good', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'awesome', 'love', 'like', 'enjoy', 'enjoyed', 'helpful', 'useful',
        'appreciate', 'appreciated', 'thanks', 'thank you', 'perfect',
        'impressed', 'happy', 'pleased', 'nice', 'beautiful', 'brilliant'
    ]
    
    def __init__(self):
        """Initialize the rule-based classifier."""
        logger.info("Initialized rule-based classifier")
    
    def classify(self, text: str) -> Tuple[str, float, str]:
        """
        Classify text using rule-based pattern matching.
        
        Args:
            text: The input text to classify
            
        Returns:
            Tuple containing:
                - label: 'question', 'comment', or 'complaint'
                - confidence: Score between 0-100
                - reason: Brief explanation for the classification
        """
        text_lower = text.lower().strip()
        
        # Calculate scores for each category
        question_score = self._calculate_question_score(text_lower)
        complaint_score = self._calculate_complaint_score(text_lower)
        comment_score = self._calculate_comment_score(text_lower)
        
        # Determine the label based on highest score
        scores = {
            'question': question_score,
            'complaint': complaint_score,
            'comment': comment_score
        }
        
        label = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[label]
        
        # Generate reason based on classification
        reason = self._generate_reason(label, text_lower)
        
        logger.debug("Rule-based classification: label=%s, confidence=%.2f", label, confidence)
        
        return label, confidence, reason
    
    def _calculate_question_score(self, text: str) -> float:
        """Calculate how likely the text is a question."""
        score = 0.0
        
        # Check for question mark (strong indicator)
        if '?' in text:
            score += 40.0
        
        # Check for question words at the beginning
        words = text.split()
        if words and words[0] in self.QUESTION_WORDS:
            score += 30.0
        
        # Check for question words anywhere in text
        question_word_count = sum(1 for word in self.QUESTION_WORDS if word in text)
        score += min(question_word_count * 5, 30.0)
        
        return min(score, 100.0)
    
    def _calculate_complaint_score(self, text: str) -> float:
        """Calculate how likely the text is a complaint."""
        score = 0.0
        
        # Check for complaint keywords
        complaint_count = sum(1 for word in self.COMPLAINT_WORDS if word in text)
        score += min(complaint_count * 20, 70.0)
        
        # Check for negative phrases (stronger indicators)
        negative_phrases = [
            "not working", "doesn't work", "won't work", "can't use",
            "not satisfied", "very disappointed", "extremely frustrated",
            "keeps crashing", "waiting for", "want a refund", "never works"
        ]
        for phrase in negative_phrases:
            if phrase in text:
                score += 25.0
        
        # Check for exclamation marks (can indicate frustration)
        if '!' in text:
            score += 15.0
        
        # Check for "I" + negative emotion (personal complaint)
        if re.search(r'\bi\s+(am|was|have been|\'m|\'ve been)\s+\w*\s*(disappointed|frustrated|upset|angry|unhappy)', text):
            score += 25.0
        
        return min(score, 100.0)
    
    def _calculate_comment_score(self, text: str) -> float:
        """Calculate how likely the text is a comment."""
        score = 30.0  # Base score for neutral statements
        
        # Check for positive words
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text)
        score += min(positive_count * 15, 50.0)
        
        # Declarative sentences (no question mark or strong emotion)
        if '?' not in text and '!' not in text:
            score += 10.0
        
        # Check for statement patterns
        statement_patterns = [
            r'\bi think\b', r'\bi believe\b', r'\bin my opinion\b',
            r'\bi feel\b', r'\bi would say\b', r'\bjust wanted to\b'
        ]
        for pattern in statement_patterns:
            if re.search(pattern, text):
                score += 10.0
        
        return min(score, 100.0)
    
    def _generate_reason(self, label: str, text: str) -> str:
        """Generate a human-readable reason for the classification."""
        if label == 'question':
            if '?' in text:
                return "Contains question mark and interrogative structure"
            else:
                return "Contains question words seeking information"
        
        elif label == 'complaint':
            complaint_found = [word for word in self.COMPLAINT_WORDS if word in text]
            if complaint_found:
                return f"Contains negative language indicating dissatisfaction ('{complaint_found[0]}')"
            else:
                return "Expresses frustration or problem with service"
        
        else:  # comment
            positive_found = [word for word in self.POSITIVE_WORDS if word in text]
            if positive_found:
                return f"Appears to be feedback or observation ('{positive_found[0]}')"
            else:
                return "Declarative statement providing feedback or opinion"


class AIClassifier:
    """
    AI-powered classifier using Hugging Face open-source models.
    
    Uses DistilBERT sentiment analysis model (local, no API key needed).
    Provides accurate classification using transformer models with better 
    context understanding and nuance detection than rule-based approaches.
    """
    
    def __init__(self):
        """Initialize the AI classifier with Hugging Face model."""
        self.sentiment_pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Hugging Face sentiment model."""
        try:
            from transformers import pipeline
            logger.info("Loading Hugging Face sentiment analysis model...")
            # Using a lightweight sentiment analysis model
            self.sentiment_pipeline = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1  # CPU (use device=0 for GPU if available)
            )
            logger.info("SUCCESS: Hugging Face DistilBERT model loaded successfully")
        except ImportError:
            logger.warning("WARNING: transformers package not installed")
            logger.info("Install with: pip install transformers torch")
            self.sentiment_pipeline = None
        except Exception as e:
            logger.error("ERROR: Could not load Hugging Face model: %s", str(e))
            self.sentiment_pipeline = None
    
    def is_available(self) -> bool:
        """Check if AI classifier is available and ready to use."""
        return self.sentiment_pipeline is not None
    
    def classify(self, text: str) -> Tuple[str, float, str]:
        """
        Classify text using Hugging Face sentiment analysis model.
        
        Args:
            text: The input text to classify
            
        Returns:
            Tuple containing:
                - label: 'question', 'comment', or 'complaint'
                - confidence: Score between 0-100
                - reason: Brief explanation for the classification
                
        Raises:
            Exception: If model inference fails
        """
        if not self.is_available():
            raise Exception("AI classifier not available - Hugging Face model not loaded")
        
        try:
            text_lower = text.lower().strip()
            
            # First, check if it's a question (high priority)
            if '?' in text:
                confidence = 85.0
                return 'question', confidence, 'Contains question mark and interrogative structure'
            
            # Check for question words at start
            question_words = ['what', 'when', 'where', 'who', 'whom', 'whose', 'which', 
                            'why', 'how', 'can', 'could', 'would', 'should', 'will', 
                            'do', 'does', 'did', 'is', 'are', 'was', 'were']
            if any(text_lower.startswith(word + ' ') for word in question_words):
                confidence = 80.0
                return 'question', confidence, 'Starts with interrogative word seeking information'
            
            # Use sentiment analysis to distinguish complaints from comments
            if self.sentiment_pipeline is None:
                raise Exception("Sentiment pipeline not initialized")
            
            sentiment_result = self.sentiment_pipeline(text, truncation=True, max_length=512)[0]
            sentiment_label = sentiment_result['label']  # POSITIVE or NEGATIVE
            sentiment_score = sentiment_result['score']  # confidence 0-1
            
            # Map sentiment to our categories
            if sentiment_label == 'NEGATIVE':
                # Check for problem/complaint indicators
                complaint_indicators = [
                    'problem', 'issue', 'broken', 'doesn\'t work', 'not working', 
                    'terrible', 'awful', 'bad', 'worst', 'frustrated', 'disappointed',
                    'hate', 'horrible', 'useless', 'never works', 'keeps crashing',
                    'want a refund', 'unacceptable', 'angry', 'upset'
                ]
                has_complaint_words = any(indicator in text_lower for indicator in complaint_indicators)
                
                if has_complaint_words or sentiment_score > 0.8:
                    confidence = min(sentiment_score * 100, 95.0)
                    return 'complaint', confidence, f'Negative sentiment with complaint indicators (model confidence: {sentiment_score:.2f})'
                else:
                    confidence = min(sentiment_score * 80, 75.0)
                    return 'complaint', confidence, f'Negative sentiment detected (model confidence: {sentiment_score:.2f})'
            
            else:  # POSITIVE or NEUTRAL
                # It's a comment (positive or neutral feedback)
                confidence = min(sentiment_score * 100, 95.0)
                positive_words = ['great', 'good', 'love', 'excellent', 'amazing', 'thanks', 
                                'appreciate', 'awesome', 'fantastic', 'wonderful']
                has_positive = any(word in text_lower for word in positive_words)
                
                if has_positive:
                    return 'comment', confidence, f'Positive sentiment detected (model confidence: {sentiment_score:.2f})'
                else:
                    return 'comment', max(confidence * 0.8, 60.0), f'Neutral observation or feedback (model confidence: {sentiment_score:.2f})'
        
        except Exception as e:
            logger.error("Hugging Face classification error: %s", str(e))
            raise Exception(f"Hugging Face classification failed: {str(e)}")


class IntentClassifier:
    """
    Main classifier that orchestrates AI and rule-based classification.
    
    Automatically falls back to rule-based approach if AI is unavailable.
    """
    
    def __init__(self):
        """Initialize both AI and rule-based classifiers."""
        logger.info("Initializing Intent Classifier")
        self.ai_classifier = AIClassifier()
        self.rule_based_classifier = RuleBasedClassifier()
    
    def classify(self, text: str) -> Tuple[str, float, str, bool]:
        """
        Classify text using the best available method.
        
        Attempts AI classification first, falls back to rules if needed.
        
        Args:
            text: The input text to classify
            
        Returns:
            Tuple containing:
                - label: 'question', 'comment', or 'complaint'
                - confidence: Score between 0-100
                - reason: Brief explanation
                - used_ai: Whether AI was used (True) or rules (False)
        """
        # Validate input
        if not text or not text.strip():
            logger.warning("Empty or invalid input received")
            return 'comment', 30.0, 'Empty or invalid input', False
        
        # Try AI classification if enabled and available
        if config.USE_AI_MODEL and self.ai_classifier.is_available():
            try:
                label, confidence, reason = self.ai_classifier.classify(text)
                return label, confidence, reason, True
            except Exception as e:
                logger.warning("AI classification failed, falling back to rules: %s", str(e))
        
        # Fall back to rule-based classification
        label, confidence, reason = self.rule_based_classifier.classify(text)
        return label, confidence, reason, False
    
    def classify_with_escalation(self, text: str) -> Dict:
        """
        Classify text and determine if escalation is needed.
        
        Args:
            text: The input text to classify
            
        Returns:
            Dictionary with keys: label, confidence, reason, escalate, method
        """
        label, confidence, reason, used_ai = self.classify(text)
        
        # Determine if escalation is needed based on confidence threshold
        escalate = confidence < config.CONFIDENCE_THRESHOLD
        
        if escalate:
            logger.info("Classification flagged for escalation: confidence=%.2f < threshold=%d",
                       confidence, config.CONFIDENCE_THRESHOLD)
        
        return {
            'label': label,
            'confidence': confidence,
            'reason': reason,
            'escalate': escalate,
            'method': 'ai' if used_ai else 'rules'
        }


# Global classifier instance
_classifier_instance = None


def get_classifier() -> IntentClassifier:
    """
    Get or create the global classifier instance.
    
    Returns:
        IntentClassifier: Singleton classifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = IntentClassifier()
    return _classifier_instance
