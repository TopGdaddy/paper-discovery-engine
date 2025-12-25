"""
daily_run.py - The Orchestrator for Daily Paper Discovery

This script coordinates all modules to work together:
1. Fetch papers from arXiv
2. Store in database
3. Score with classifier
4. Send email notification
"""

import sys
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any

# Add src to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

# Import our modules
from scraper import ArXivScraper
from database import DatabaseManager
from classifier import PaperClassifier
from notifier import EmailNotifier


# =============================================================================
# CONFIGURATION - Default settings
# =============================================================================

DEFAULT_CONFIG = {
    'categories': ['cs.AI', 'cs.LG', 'cs.CL'],
    'papers_per_category': 25,
    'email_threshold': 0.50,
    'send_email': True,
    'database_path': 'data/papers.db',
}


# =============================================================================
# HELPER FUNCTIONS FOR NICE OUTPUT
# =============================================================================

def print_header(title: str) -> None:
    """Print a section header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(num: int, title: str) -> None:
    """Print a step header."""
    print()
    print(f"─" * 70)
    print(f"  STEP {num}: {title}")
    print(f"─" * 70)


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def run_daily_workflow(
    categories: List[str] = None,
    papers_per_category: int = None,
    email_threshold: float = None,
    send_email: bool = None,
    database_path: str = None,
) -> Dict[str, Any]:
    """
    Run the complete daily paper discovery workflow.
    
    This is the MAIN function that orchestrates everything.
    """
    
    # Use defaults if not provided
    categories = categories or DEFAULT_CONFIG['categories']
    papers_per_category = papers_per_category or DEFAULT_CONFIG['papers_per_category']
    email_threshold = email_threshold if email_threshold is not None else DEFAULT_CONFIG['email_threshold']
    send_email = send_email if send_email is not None else DEFAULT_CONFIG['send_email']
    database_path = database_path or DEFAULT_CONFIG['database_path']
    
    # Track results
    results = {
        'started_at': datetime.now().isoformat(),
        'papers_fetched': 0,
        'papers_new': 0,
        'papers_scored': 0,
        'email_sent': False,
        'success': True,
    }
    
    # =========================================================================
    # HEADER
    # =========================================================================
    
    print_header("PAPER DISCOVERY ENGINE - Daily Run")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Categories: {', '.join(categories)}")
    
    # =========================================================================
    # STEP 1: INITIALIZE
    # =========================================================================
    
    print_step(1, "Initialize Modules")
    
    try:
        print("  Loading scraper...")
        scraper = ArXivScraper()
        print("  ✅ Scraper ready")
        
        print("  Connecting to database...")
        db = DatabaseManager(database_path)
        print(f"  ✅ Database connected ({db.count_papers()} papers)")
        
        print("  Loading classifier...")
        classifier = PaperClassifier()
        classifier_loaded = classifier.load()
        if classifier_loaded:
            print(f"  ✅ Classifier ready")
        else:
            print("  ⚠️  No classifier found (papers won't be scored)")
        
        print("  Setting up email...")
        notifier = EmailNotifier()
        if notifier.is_configured:
            print(f"  ✅ Email ready ({notifier.email})")
        else:
            print("  ⚠️  Email not configured")
            send_email = False
            
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        results['success'] = False
        return results
    
    # =========================================================================
    # STEP 2: FETCH PAPERS
    # =========================================================================
    
    print_step(2, "Fetch Papers from arXiv")
    
    all_papers = []
    
    for category in categories:
        print(f"\n  📂 Fetching {category}...")
        
        try:
            papers = scraper.get_latest_papers(
                category=category,
                count=papers_per_category
            )
            
            if papers:
                all_papers.extend(papers)
                print(f"     ✅ Got {len(papers)} papers")
            else:
                print(f"     ⚠️  No papers returned")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    results['papers_fetched'] = len(all_papers)
    print(f"\n  📊 Total fetched: {len(all_papers)} papers")
    
    if not all_papers:
        print("  ❌ No papers fetched!")
        db.close()
        results['success'] = False
        return results
    
    # =========================================================================
    # STEP 3: STORE IN DATABASE
    # =========================================================================
    
    print_step(3, "Store in Database")
    
    try:
        result = db.add_papers(all_papers)
        new_count = result.get('added', 0)
        skipped = result.get('skipped', 0)
        
        results['papers_new'] = new_count
        
        print(f"  ✅ Added {new_count} new papers")
        print(f"  ⏭️  Skipped {skipped} duplicates")
        print(f"  📁 Total in database: {db.count_papers()}")
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")
    
    # =========================================================================
    # STEP 4: SCORE PAPERS
    # =========================================================================
    
    print_step(4, "Score Papers with Classifier")
    
    if not classifier_loaded:
        print("  ⚠️  Skipping (no classifier)")
    else:
        try:
            # Get unscored papers
            all_db_papers = db.get_all_papers(limit=500)
            unscored = [p for p in all_db_papers if p.relevance_score == 0.0]
            
            if unscored:
                print(f"  Scoring {len(unscored)} papers...")
                
                # Convert to dicts
                papers_data = [p.to_dict() for p in unscored]
                
                # Predict
                scores = classifier.predict(papers_data)
                
                # Update database
                score_dict = {
                    papers_data[i]['arxiv_id']: scores[i]
                    for i in range(len(scores))
                }
                updated = db.update_scores_bulk(score_dict)
                
                results['papers_scored'] = updated
                print(f"  ✅ Scored {updated} papers")
            else:
                print("  ✅ All papers already scored")
                
        except Exception as e:
            print(f"  ❌ Scoring error: {e}")
    
    # =========================================================================
    # STEP 5: SEND EMAIL
    # =========================================================================
    
    print_step(5, "Send Email Notification")
    
    if not send_email:
        print("  ⏭️  Skipping (disabled)")
    elif not notifier.is_configured:
        print("  ⏭️  Skipping (not configured)")
    else:
        try:
            # Get papers for email
            all_db_papers = db.get_all_papers(limit=100)
            top_papers = [
                p for p in all_db_papers
                if p.relevance_score >= email_threshold
            ]
            
            if not top_papers:
                print(f"  ℹ️  No papers above {email_threshold:.0%} threshold")
            else:
                print(f"  📧 Sending {len(top_papers[:10])} papers...")
                
                success = notifier.send_daily_digest(
                    papers=all_db_papers,
                    min_score=email_threshold
                )
                
                if success:
                    results['email_sent'] = True
                    print(f"  ✅ Email sent!")
                else:
                    print(f"  ❌ Email failed")
                    
        except Exception as e:
            print(f"  ❌ Email error: {e}")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    
    print_header("COMPLETE!")
    
    print(f"  📊 Results:")
    print(f"     Papers fetched: {results['papers_fetched']}")
    print(f"     New papers:     {results['papers_new']}")
    print(f"     Papers scored:  {results['papers_scored']}")
    print(f"     Email sent:     {'✅ Yes' if results['email_sent'] else '❌ No'}")
    print()
    
    # Cleanup
    db.close()
    
    return results


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

def main():
    """Entry point with command-line arguments."""
    
    parser = argparse.ArgumentParser(
        description='Daily Paper Discovery Workflow'
    )
    
    parser.add_argument(
        '--categories',
        nargs='+',
        default=DEFAULT_CONFIG['categories'],
        help='arXiv categories to fetch'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=DEFAULT_CONFIG['papers_per_category'],
        help='Papers per category'
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        default=DEFAULT_CONFIG['email_threshold'],
        help='Minimum score for email'
    )
    
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Skip email notification'
    )
    
    args = parser.parse_args()
    
    # Run workflow
    results = run_daily_workflow(
        categories=args.categories,
        papers_per_category=args.count,
        email_threshold=args.threshold,
        send_email=not args.no_email,
    )
    
    # Exit code
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main()