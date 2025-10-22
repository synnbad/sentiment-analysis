"""
Demo script to showcase the classifier with interesting examples.

Run this to demonstrate the classifier's capabilities interactively.
"""
from src.modeling.predict import get_classifier
from src.config import config
import time


def print_header():
    """Print demo header."""
    print("\n" + "=" * 80)
    print(" " * 20 + "SENTIMENT ANALYSIS - INTENT TRIAGE DEMO")
    print("=" * 80)
    print("\nWelcome! This demo showcases the intent classification system.")
    print("It can classify messages as: QUESTION | COMMENT | COMPLAINT\n")


def print_classification(text: str, result: dict):
    """Pretty print a classification result."""
    print(f"\nInput: \"{text}\"")
    print("-" * 80)
    
    # Label
    label_display = result['label'].upper()
    
    print(f"\nClassification: {label_display}")
    print(f"Confidence: {result['confidence']:.1f}%")
    
    # Visual confidence bar
    bar_length = int(result['confidence'] / 2)
    bar = "=" * bar_length + "-" * (50 - bar_length)
    print(f"    [{bar}]")
    
    print(f"Reason: {result['reason']}")
    
    if result['escalate']:
        print(f"ESCALATE: Yes - Low confidence, needs human review")
    else:
        print(f"ESCALATE: No - High confidence")
    
    print(f"Method: {result['method'].upper()}")
    print("-" * 80)


def run_demo():
    """Run the interactive demo."""
    print_header()
    
    # Get classifier
    classifier = get_classifier()
    
    # Check if AI is available
    ai_available = config.USE_AI_MODEL and classifier.ai_classifier.is_available()
    if ai_available:
        print("[SUCCESS] AI Model: ENABLED (Hugging Face DistilBERT)")
    else:
        print("[INFO] AI Model: DISABLED (Using rule-based fallback)")
    
    print(f"[INFO] Confidence Threshold: {config.CONFIDENCE_THRESHOLD}%")
    print("\n" + "=" * 80)
    
    # Demo examples categorized by type
    examples = {
        "Clear Questions": [
            "How do I reset my password?",
            "What time does the store close?",
            "Can you help me with this error?",
        ],
        "Positive Comments": [
            "I really love the new features!",
            "Great job on the update.",
            "This has been very helpful, thank you!",
        ],
        "Obvious Complaints": [
            "This is terrible and never works!",
            "Very disappointed with the service.",
            "The app keeps crashing constantly.",
        ],
        "Ambiguous Cases": [
            "Why is this so bad?",
            "Can someone please fix this bug?",
            "I'm not sure if this is working correctly.",
        ]
    }
    
    # Run through categories
    for category, texts in examples.items():
        print(f"\n{'='*80}")
        print(f"  {category.upper()}")
        print(f"{'='*80}")
        
        for text in texts:
            time.sleep(0.5)  # Small delay for dramatic effect
            result = classifier.classify_with_escalation(text)
            print_classification(text, result)
            
            # Pause between examples
            if texts.index(text) < len(texts) - 1:
                input("\nPress Enter for next example...")
    
    # Interactive section
    print(f"\n{'='*80}")
    print("  INTERACTIVE MODE")
    print(f"{'='*80}")
    print("\nNow try your own examples! (Type 'quit' to exit)\n")
    
    while True:
        try:
            text = input("\nEnter text to classify: ").strip()
            
            if not text:
                continue
            
            if text.lower() in ['quit', 'exit', 'q']:
                print("\nThanks for trying the demo!\n")
                break
            
            result = classifier.classify_with_escalation(text)
            print_classification(text, result)
            
        except (KeyboardInterrupt, EOFError):
            print("\n\nThanks for trying the demo!\n")
            break
    
    # Summary
    print("\n" + "=" * 80)
    print("  DEMO SUMMARY")
    print("=" * 80)
    print("\n[SUCCESS] Demonstrated classification of questions, comments, and complaints")
    print("[SUCCESS] Showed confidence scoring and escalation logic")
    print("[SUCCESS] Handled clear and ambiguous examples")
    print("\nFor more information:")
    print("   - View API docs: http://localhost:8000/docs")
    print("   - Try web demo: http://localhost:8000/static/index.html")
    print("   - Run evaluation: python scripts/evaluate_model.py")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    run_demo()
