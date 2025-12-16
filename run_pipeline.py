"""
run_pipeline.py - Main script to run the complete pipeline

This fetches papers from arXiv and stores them in the database.
Run this daily to get new papers!
"""

import sys
import os

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import ArXivScraper
from database import DatabaseManager


def main():
    """Run the paper discovery pipeline."""
    
    print("=" * 80)
    print("🚀 PAPER DISCOVERY ENGINE - Daily Pipeline")
    print("=" * 80)
    
    # Initialize components
    scraper = ArXivScraper(max_results=20)
    db = DatabaseManager("data/papers.db")
    
    # Categories to fetch
    categories = ["cs.AI", "cs.LG", "cs.CL"]
    
    total_added = 0
    total_skipped = 0
    
    # Fetch from each category
    for category in categories:
        print(f"\n{'─' * 40}")
        papers = scraper.get_latest_papers(category=category, count=15)
        
        if papers:
            result = db.add_papers(papers)
            total_added += result['added']
            total_skipped += result['skipped']
    
    # Show results
    print("\n" + "=" * 80)
    print("📊 PIPELINE RESULTS")
    print("=" * 80)
    
    print(f"\n   📥 New papers added: {total_added}")
    print(f"   ⏭️  Duplicates skipped: {total_skipped}")
    
    stats = db.get_stats()
    print(f"\n   📁 Total in database: {stats['total_papers']}")
    print(f"   🏷️  Labeled: {stats['labeled_papers']}")
    print(f"   📂 Categories: {', '.join(stats['categories'])}")
    
    # Show 5 newest papers
    print("\n📚 NEWEST PAPERS:")
    print("─" * 80)
    
    recent = db.get_all_papers(limit=5)
    for i, paper in enumerate(recent, 1):
        print(f"\n{i}. {paper.title[:70]}...")
        print(f"   🆔 {paper.arxiv_id}")
        print(f"   📂 {paper.primary_category}")
        print(f"   🔗 {paper.abs_url}")
    
    db.close()
    
    print("\n" + "=" * 80)
    print("✅ Pipeline complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()