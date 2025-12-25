"""
label_papers.py - Interactive paper labeling tool

Run this to label papers in your database!
These labels will be used to train the classifier.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import DatabaseManager
from classifier import label_papers_interactive


def main():
    print("=" * 60)
    print("🏷️  PAPER LABELING TOOL")
    print("=" * 60)
    
    # Connect to database
    db = DatabaseManager("data/papers.db")
    
    # Get stats
    stats = db.get_stats()
    print(f"\n📊 Database Status:")
    print(f"   Total papers: {stats['total_papers']}")
    print(f"   Already labeled: {stats['labeled_papers']}")
    print(f"   Unlabeled: {stats['unlabeled_papers']}")
    
    if stats['unlabeled_papers'] == 0:
        print("\n✅ All papers are already labeled!")
        db.close()
        return
    
    # Get unlabeled papers
    unlabeled = db.get_unlabeled_papers(limit=10)
    print(f"\n📄 Fetched {len(unlabeled)} unlabeled papers to label.")
    
    # Convert to dictionaries for labeling
    papers_to_label = [p.to_dict() for p in unlabeled]
    
    # Interactive labeling
    labeled = label_papers_interactive(papers_to_label)
    
    # Save labels to database
    if labeled:
        print(f"\n💾 Saving {len(labeled)} labels to database...")
        for paper in labeled:
            db.label_paper(paper['arxiv_id'], paper['user_label'])
    
    # Show updated stats
    new_stats = db.get_stats()
    print(f"\n📊 Updated Status:")
    print(f"   Labeled: {new_stats['labeled_papers']} ({new_stats['positive_labels']} 👍, {new_stats['negative_labels']} 👎)")
    print(f"   Remaining: {new_stats['unlabeled_papers']}")
    
    db.close()
    
    print("\n✅ Labeling complete!")


if __name__ == "__main__":
    main()