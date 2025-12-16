"""
run_pipeline.py - Main pipeline with proper rate limiting
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import ArXivScraper
from database import DatabaseManager


def main():
    """Run the paper discovery pipeline."""
    
    print("=" * 80)
    print("🚀 PAPER DISCOVERY ENGINE - Daily Pipeline")
    print("=" * 80)
    
    # Initialize
    scraper = ArXivScraper(max_results=20)
    db = DatabaseManager("data/papers.db")
    
    # Categories to fetch (fewer to avoid rate limits)
    categories = ["cs.AI", "cs.LG", "cs.CL"]
    
    total_added = 0
    total_skipped = 0
    
    for i, category in enumerate(categories):
        print(f"\n{'─' * 40}")
        print(f"📂 Category {i+1}/{len(categories)}: {category}")
        print(f"{'─' * 40}")
        
        # Fetch papers (scraper handles rate limiting internally)
        papers = scraper.get_latest_papers(category=category, count=10)
        
        if papers:
            result = db.add_papers(papers)
            total_added += result['added']
            total_skipped += result['skipped']
        else:
            print("   ⚠️ No papers fetched (might be rate limited)")
    
    # Results
    print("\n" + "=" * 80)
    print("📊 PIPELINE RESULTS")
    print("=" * 80)
    
    print(f"\n   📥 New papers added: {total_added}")
    print(f"   ⏭️  Duplicates skipped: {total_skipped}")
    print(f"   🔢 Total API requests: {scraper.get_request_count()}")
    
    stats = db.get_stats()
    print(f"\n   📁 Total in database: {stats['total_papers']}")
    print(f"   🏷️  Labeled: {stats['labeled_papers']}")
    
    if stats['categories']:
        print(f"   📂 Categories: {', '.join(stats['categories'])}")
    
    # Show newest papers
    print("\n📚 NEWEST PAPERS:")
    print("─" * 80)
    
    recent = db.get_all_papers(limit=5)
    for i, paper in enumerate(recent, 1):
        title = paper.title[:65] + "..." if len(paper.title) > 65 else paper.title
        print(f"\n{i}. {title}")
        print(f"   🆔 {paper.arxiv_id}")
        print(f"   📂 {paper.primary_category}")
    
    db.close()
    
    print("\n" + "=" * 80)
    print("✅ Pipeline complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()