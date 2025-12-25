"""
train_classifier.py - Train the classifier on your labeled papers

Run this after labeling at least 5 papers!
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import DatabaseManager
from classifier import PaperClassifier


def main():
    print("=" * 60)
    print("🎓 TRAIN CLASSIFIER")
    print("=" * 60)
    
    # Connect to database
    db = DatabaseManager("data/papers.db")
    
    # Get labeled papers
    labeled_papers = db.get_labeled_papers()
    
    print(f"\n📊 Found {len(labeled_papers)} labeled papers")
    
    if len(labeled_papers) < 5:
        print(f"\n❌ Need at least 5 labeled papers to train!")
        print(f"   Run: python label_papers.py")
        db.close()
        return
    
    # Convert to dicts
    papers_data = [p.to_dict() for p in labeled_papers]
    
    # Count labels
    positive = sum(1 for p in papers_data if p['user_label'] == 1)
    negative = len(papers_data) - positive
    print(f"   👍 Relevant: {positive}")
    print(f"   👎 Not relevant: {negative}")
    
    # Initialize and train classifier
    classifier = PaperClassifier()
    result = classifier.train(papers_data)
    
    if result['success']:
        # Save the trained model
        classifier.save()
        
        print(f"\n✅ Classifier trained and saved!")
        print(f"   Accuracy: {result['accuracy']:.1%}")
    else:
        print(f"\n❌ Training failed: {result.get('error', 'Unknown error')}")
    
    db.close()


if __name__ == "__main__":
    main()