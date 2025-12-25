"""
daily_digest.py - Scheduled job for GitHub Actions
"""

import os
import sys
from pathlib import Path
from datetime import datetime

SRC_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SRC_DIR))

from database import DatabaseManager, PaperRecord
from email_service import EmailDigestService
import feedparser
import requests
import time


def fetch_new_papers(db, categories=None, max_results=30):
    if categories is None:
        categories = ['cs.AI', 'cs.LG']
    
    print(f"📡 Fetching from: {categories}")
    headers = {'User-Agent': 'PaperDiscoveryBot/1.0'}
    count = 0
    
    for cat in categories:
        url = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&max_results={max_results}&sortBy=submittedDate"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries:
                arxiv_id = entry.id.split('/abs/')[-1]
                
                if db.get_paper_by_id(arxiv_id):
                    continue
                
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                
                paper = PaperRecord(
                    arxiv_id=arxiv_id,
                    title=entry.title.replace('\n', ' '),
                    authors=', '.join([a.name for a in entry.authors]) if hasattr(entry, 'authors') else "Unknown",
                    summary=entry.summary.replace('\n', ' '),
                    pdf_url=f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                    abs_url=entry.link,
                    primary_category=entry.tags[0].term if entry.tags else cat,
                    published=published,
                    fetched_at=datetime.utcnow(),
                    relevance_score=0.5
                )
                
                try:
                    db.session.add(paper)
                    db.session.commit()
                    count += 1
                except:
                    db.session.rollback()
            
            time.sleep(3)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"📚 Added {count} new papers")
    return count


def main():
    print("=" * 50)
    print("🚀 DAILY DIGEST JOB")
    print(f"⏰ {datetime.utcnow()}")
    print("=" * 50)
    
    db = DatabaseManager()
    email_service = EmailDigestService(db)
    
    if os.environ.get('SMTP_USER'):
        email_service.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        email_service.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        email_service.smtp_user = os.environ.get('SMTP_USER')
        email_service.smtp_password = os.environ.get('SMTP_PASSWORD')
        email_service.from_email = os.environ.get('SMTP_USER')
    
    prefs = db.get_preferences()
    categories = prefs.get_tracked_categories() or ['cs.AI', 'cs.LG']
    
    print("\n📡 Fetching papers...")
    fetch_new_papers(db, categories)
    
    print("\n📧 Sending digest...")
    if prefs.email and prefs.digest_enabled:
        papers = db.get_papers_for_digest(since_days=1)
        if papers:
            success, msg = email_service.send_digest(prefs.email, papers, 'daily')
            print(f"{'✅' if success else '❌'} {msg}")
        else:
            print("📭 No new papers")
    else:
        print("⏸️ Digest disabled or no email")
    
    print("\n✅ DONE")


if __name__ == "__main__":
    main()
