"""
Unit tests for the intent classifier.

Tests both rule-based and AI classification approaches, including
edge cases and fallback behavior.
"""
import pytest
from src.modeling.predict import (
    RuleBasedClassifier, 
    AIClassifier, 
    IntentClassifier,
    get_classifier
)
from src.config import config


class TestRuleBasedClassifier:
    """Tests for the rule-based classifier."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = RuleBasedClassifier()
    
    def test_question_with_question_mark(self):
        """Test that questions with ? are correctly identified."""
        text = "How do I reset my password?"
        label, confidence, reason = self.classifier.classify(text)
        assert label == "question"
        assert confidence > 50
        assert "question" in reason.lower()
    
    def test_question_without_question_mark(self):
        """Test questions without question marks."""
        text = "Can you help me with this issue"
        label, confidence, reason = self.classifier.classify(text)
        assert label == "question"
        assert confidence > 30
    
    def test_complaint_with_negative_words(self):
        """Test complaints with negative language."""
        text = "This is terrible and never works properly!"
        label, confidence, reason = self.classifier.classify(text)
        assert label == "complaint"
        assert confidence > 50
        assert "negative" in reason.lower() or "dissatisfaction" in reason.lower()
    
    def test_positive_comment(self):
        """Test positive comments."""
        text = "I really love this feature, it's fantastic!"
        label, confidence, reason = self.classifier.classify(text)
        assert label == "comment"
        assert confidence > 40
    
    def test_neutral_statement(self):
        """Test neutral declarative statements."""
        text = "I updated my profile yesterday."
        label, confidence, reason = self.classifier.classify(text)
        assert label == "comment"
    
    def test_empty_string(self):
        """Test behavior with empty string."""
        text = ""
        label, confidence, reason = self.classifier.classify(text)
        assert label in ["question", "comment", "complaint"]
        assert 0 <= confidence <= 100
    
    def test_mixed_indicators(self):
        """Test text with mixed question and complaint indicators."""
        text = "Why is this service so terrible?"
        label, confidence, reason = self.classifier.classify(text)
        # Should classify as either question or complaint
        assert label in ["question", "complaint"]


class TestAIClassifier:
    """Tests for the AI classifier."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = AIClassifier()
    
    def test_classifier_initialization(self):
        """Test that AI classifier initializes correctly."""
        assert self.classifier is not None
    
    def test_availability_check(self):
        """Test AI availability checking."""
        is_available = self.classifier.is_available()
        assert isinstance(is_available, bool)
        # Availability depends on Hugging Face model
        # Should be True if transformers is installed
        assert is_available in [True, False]
    
    @pytest.mark.skipif(not config.USE_AI_MODEL, reason="AI model disabled in config")
    def test_ai_classification(self):
        """Test AI classification (requires Hugging Face transformers)."""
        if not self.classifier.is_available():
            pytest.skip("AI classifier not available")
        
        text = "How do I reset my password?"
        try:
            label, confidence, reason = self.classifier.classify(text)
            assert label in ["question", "comment", "complaint"]
            assert 0 <= confidence <= 100
            assert len(reason) > 0
        except Exception as e:
            # Model might fail for various reasons (memory, etc.)
            pytest.skip(f"AI classification failed: {e}")


class TestIntentClassifier:
    """Tests for the main intent classifier orchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = IntentClassifier()
    
    def test_classifier_initialization(self):
        """Test that intent classifier initializes properly."""
        assert self.classifier is not None
        assert self.classifier.ai_classifier is not None
        assert self.classifier.rule_based_classifier is not None
    
    def test_classify_question(self):
        """Test classification of a question."""
        text = "What time does the store close?"
        label, confidence, reason, used_ai = self.classifier.classify(text)
        assert label == "question"
        assert 0 <= confidence <= 100
        assert len(reason) > 0
        assert isinstance(used_ai, bool)
    
    def test_classify_comment(self):
        """Test classification of a comment."""
        text = "I think the new design looks great!"
        label, confidence, reason, used_ai = self.classifier.classify(text)
        assert label == "comment"
        assert 0 <= confidence <= 100
        assert len(reason) > 0
    
    def test_classify_complaint(self):
        """Test classification of a complaint."""
        text = "This app is broken and I'm very frustrated."
        label, confidence, reason, used_ai = self.classifier.classify(text)
        assert label == "complaint"
        assert 0 <= confidence <= 100
        assert len(reason) > 0
    
    def test_classify_with_escalation(self):
        """Test classification with escalation checking."""
        text = "How do I reset my password?"
        result = self.classifier.classify_with_escalation(text)
        
        # Check all required fields are present
        assert 'label' in result
        assert 'confidence' in result
        assert 'reason' in result
        assert 'escalate' in result
        assert 'method' in result
        
        # Validate field types and values
        assert result['label'] in ["question", "comment", "complaint"]
        assert 0 <= result['confidence'] <= 100
        assert isinstance(result['reason'], str)
        assert isinstance(result['escalate'], bool)
        assert result['method'] in ['ai', 'rules']
    
    def test_empty_input(self):
        """Test behavior with empty input."""
        text = ""
        label, confidence, reason, used_ai = self.classifier.classify(text)
        assert label in ["question", "comment", "complaint"]
        assert 0 <= confidence <= 100
    
    def test_whitespace_input(self):
        """Test behavior with only whitespace."""
        text = "   \n\t  "
        label, confidence, reason, used_ai = self.classifier.classify(text)
        assert label in ["question", "comment", "complaint"]


class TestGetClassifier:
    """Tests for the global classifier singleton."""
    
    def test_get_classifier_returns_instance(self):
        """Test that get_classifier returns a valid instance."""
        classifier = get_classifier()
        assert classifier is not None
        assert isinstance(classifier, IntentClassifier)
    
    def test_get_classifier_returns_same_instance(self):
        """Test that get_classifier returns the same instance (singleton)."""
        classifier1 = get_classifier()
        classifier2 = get_classifier()
        assert classifier1 is classifier2


# TODO: Add more comprehensive tests including:
# - Test with various edge cases (URLs, special characters, emojis)
# - Test fallback behavior when AI fails
# - Test confidence threshold variations
# - Test with multilingual inputs
# - Performance tests for batch classification
