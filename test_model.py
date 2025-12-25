"""
test_model.py - Diagnose why the classifier isn't working well

WHAT THIS DOES:
===============
1. Loads your trained classifier
2. Tests it on ALL your labeled papers (not just the test set)
3. Shows you exactly where it's confused
4. Calculates score distributions

WHY WE NEED THIS:
=================
The 50% accuracy was on a TINY test set (8 papers).
We need to see the FULL picture to understand what's wrong.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import DatabaseManager
from classifier import PaperClassifier


def main():
    print("=" * 70)
    print("🔍 CLASSIFIER DIAGNOSTIC REPORT")
    print("=" * 70)
    
    # =========================================================================
    # STEP 1: Load the trained classifier
    # =========================================================================
    print("\n📂 Loading classifier...")
    classifier = PaperClassifier()
    
    if not classifier.load():
        print("❌ No trained classifier found!")
        print("   Run: python train_classifier.py first")
        return
    
    # =========================================================================
    # STEP 2: Get all labeled papers from database
    # =========================================================================
    print("\n📂 Loading labeled papers from database...")
    db = DatabaseManager("data/papers.db")
    labeled_papers = db.get_labeled_papers()
    
    print(f"   Found {len(labeled_papers)} labeled papers")
    
    # Count labels
    relevant_count = sum(1 for p in labeled_papers if p.user_label == 1)
    not_relevant_count = len(labeled_papers) - relevant_count
    print(f"   👍 Relevant: {relevant_count}")
    print(f"   👎 Not Relevant: {not_relevant_count}")
    
    # =========================================================================
    # STEP 3: Get predictions for ALL labeled papers
    # =========================================================================
    print("\n🧠 Getting predictions for all papers...")
    
    results = []
    
    for paper in labeled_papers:
        # Convert database object to dictionary
        paper_dict = paper.to_dict()
        
        # What YOU labeled it as
        actual_label = paper_dict['user_label']
        
        # What the MODEL thinks (0.0 to 1.0)
        predicted_score = classifier.predict_single(paper_dict)
        
        # Model's decision: >0.5 = relevant, <0.5 = not relevant
        predicted_label = 1 if predicted_score > 0.5 else 0
        
        # Is the model correct?
        is_correct = (actual_label == predicted_label)
        
        results.append({
            'title': paper_dict['title'],
            'category': paper_dict.get('primary_category', 'unknown'),
            'actual': actual_label,
            'predicted': predicted_label,
            'score': predicted_score,
            'correct': is_correct
        })
    
    # =========================================================================
    # STEP 4: Calculate accuracy on ALL data
    # =========================================================================
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    accuracy = correct_count / total_count * 100
    
    print("\n" + "=" * 70)
    print("📊 ACCURACY ON ALL LABELED DATA")
    print("=" * 70)
    print(f"\n   🎯 Accuracy: {accuracy:.1f}%")
    print(f"   ✅ Correct: {correct_count}")
    print(f"   ❌ Wrong: {total_count - correct_count}")
    
    # =========================================================================
    # STEP 5: Analyze score distributions
    # =========================================================================
    # This is KEY - we want to see if the model gives different scores
    # to relevant vs not relevant papers
    
    relevant_scores = [r['score'] for r in results if r['actual'] == 1]
    not_relevant_scores = [r['score'] for r in results if r['actual'] == 0]
    
    print("\n" + "=" * 70)
    print("📊 SCORE DISTRIBUTIONS (This is the key insight!)")
    print("=" * 70)
    
    if relevant_scores:
        avg_relevant = sum(relevant_scores) / len(relevant_scores)
        min_relevant = min(relevant_scores)
        max_relevant = max(relevant_scores)
        
        print(f"\n   👍 RELEVANT papers (n={len(relevant_scores)}):")
        print(f"      Average score: {avg_relevant:.1%}")
        print(f"      Range: {min_relevant:.1%} to {max_relevant:.1%}")
    
    if not_relevant_scores:
        avg_not_relevant = sum(not_relevant_scores) / len(not_relevant_scores)
        min_not_relevant = min(not_relevant_scores)
        max_not_relevant = max(not_relevant_scores)
        
        print(f"\n   👎 NOT RELEVANT papers (n={len(not_relevant_scores)}):")
        print(f"      Average score: {avg_not_relevant:.1%}")
        print(f"      Range: {min_not_relevant:.1%} to {max_not_relevant:.1%}")
    
    # =========================================================================
    # STEP 6: Show the GAP between classes
    # =========================================================================
    if relevant_scores and not_relevant_scores:
        gap = avg_relevant - avg_not_relevant
        
        print(f"\n   📏 GAP between classes: {gap:.1%}")
        
        print("\n   " + "-" * 50)
        if gap > 0.3:
            print("   ✅ Good separation! The model can distinguish classes.")
        elif gap > 0.1:
            print("   ⚠️  Some separation, but not great. Need more diverse data.")
        else:
            print("   ❌ Almost NO separation! The model is confused.")
            print("      This is why accuracy is ~50% (random guessing).")
    
    # =========================================================================
    # STEP 7: Show wrong predictions
    # =========================================================================
    wrong_predictions = [r for r in results if not r['correct']]
    
    print("\n" + "=" * 70)
    print(f"❌ WRONG PREDICTIONS ({len(wrong_predictions)} total)")
    print("=" * 70)
    
    if wrong_predictions:
        for i, r in enumerate(wrong_predictions[:10], 1):  # Show first 10
            actual_emoji = "👍" if r['actual'] == 1 else "👎"
            pred_emoji = "👍" if r['predicted'] == 1 else "👎"
            
            print(f"\n   {i}. {r['title'][:55]}...")
            print(f"      Category: {r['category']}")
            print(f"      You said: {actual_emoji} | Model said: {pred_emoji} [{r['score']:.0%}]")
        
        if len(wrong_predictions) > 10:
            print(f"\n   ... and {len(wrong_predictions) - 10} more wrong predictions")
    else:
        print("\n   🎉 No wrong predictions! Model is perfect!")
    
    # =========================================================================
    # STEP 8: Show correct predictions (sample)
    # =========================================================================
    correct_predictions = [r for r in results if r['correct']]
    
    print("\n" + "=" * 70)
    print(f"✅ CORRECT PREDICTIONS (showing 5 examples)")
    print("=" * 70)
    
    for i, r in enumerate(correct_predictions[:5], 1):
        emoji = "👍" if r['actual'] == 1 else "👎"
        print(f"\n   {i}. {emoji} [{r['score']:.0%}] {r['title'][:50]}...")
    
    # =========================================================================
    # STEP 9: DIAGNOSIS
    # =========================================================================
    print("\n" + "=" * 70)
    print("🩺 DIAGNOSIS & RECOMMENDATION")
    print("=" * 70)
    
    if accuracy >= 80:
        print("\n   ✅ Your model is working well!")
        print("   💡 You can now run: python score_papers.py")
        
    elif accuracy >= 65:
        print("\n   ⚠️  Model is learning, but needs improvement.")
        print("\n   💡 Recommendations:")
        print("      1. Label 20-30 more papers")
        print("      2. Make sure you have diverse 'not relevant' examples")
        print("      3. Retrain with: python train_classifier.py")
        
    else:
        print("\n   ❌ Model is struggling (similar to random guessing).")
        print("\n   🔍 ROOT CAUSE:")
        
        if relevant_scores and not_relevant_scores:
            if abs(avg_relevant - avg_not_relevant) < 0.15:
                print("      The model sees all papers as SIMILAR!")
                print("      This happens when all papers are from the same field.")
                print("\n   💡 SOLUTION:")
                print("      Add papers from COMPLETELY DIFFERENT fields as 'not relevant':")
                print("      - Biology papers")
                print("      - Economics papers")  
                print("      - Physics papers")
                print("      - Medical papers")
                print("\n   📝 Run: python add_diverse_training.py")
                print("      Then: python train_classifier.py")
    
    db.close()
    
    print("\n" + "=" * 70)
    print("📋 DIAGNOSTIC COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()