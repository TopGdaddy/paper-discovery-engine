"""
score_papers.py - Score all papers using the trained classifier

Run this after training to score all papers!
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import DatabaseManager
from classifier import PaperClassifier


def main():
    print("=" * 60)
    print("🎯 SCORE PAPERS")
    print("=" * 60)
    
    # Connect to database
    db = DatabaseManager("data/papers.db")
    
    # Load classifier
    classifier = PaperClassifier()
    if not classifier.load():
        print("\n❌ No trained classifier found!")
        print("   Run: python train_classifier.py")
        db.close()
        return
    
    # Get all papers
    all_papers = db.get_all_papers(limit=1000)
    print(f"\n📄 Scoring {len(all_papers)} papers...")
    
    # Convert to dicts
    papers_data = [p.to_dict() for p in all_papers]
    
    # Predict scores
    scores = classifier.predict(papers_data)
    
    # Update database
    scores_dict = {p['arxiv_id']: score for p, score in zip(papers_data, scores)}
    updated = db.update_scores_bulk(scores_dict)
    print(f"✅ Updated scores for {updated} papers")
    
    # Show top papers
    print("\n🏆 TOP 5 PAPERS (Most Relevant):")
    print("-" * 60)
    
    top_papers = db.get_top_papers(limit=5, min_score=0.0)
    for i, paper in enumerate(top_papers, 1):
        score = paper.relevance_score
        emoji = "🔥" if score > 0.8 else "👍" if score > 0.5 else "🤷"
        print(f"\n{i}. {emoji} [{score:.1%}] {paper.title[:55]}...")
        print(f"      📂 {paper.primary_category} | 🔗 {paper.abs_url}")
    
    db.close()
    
    print("\n✅ Scoring complete!")


if __name__ == "__main__":
    main()