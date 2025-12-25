"""
scheduler.py - Background scheduler for automated digest sending
Run: python src/scheduler.py
"""

import schedule
import time
from datetime import datetime
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SRC_DIR))

from database import DatabaseManager
from email_service import EmailDigestService

DB_PATH = SRC_DIR.parent / "data" / "papers.db"


def check_and_send_digest():
    """Check if it's time to send digest"""
    print(f"[{datetime.now()}] Checking digest schedule...")
    
    db = DatabaseManager(str(DB_PATH))
    prefs = db.get_preferences()
    
    if not prefs.digest_enabled or not prefs.email:
        print("Digest disabled or no email set")
        return
    
    now = datetime.utcnow()
    history = db.get_digest_history(limit=1)
    
    should_send = False
    
    if prefs.digest_frequency == 'daily':
        if history:
            last_sent = history[0].sent_at
            if last_sent.date() < now.date():
                should_send = True
        else:
            should_send = True
            
    elif prefs.digest_frequency == 'weekly':
        if history:
            days_since = (now - history[0].sent_at).days
            if days_since >= 7:
                should_send = True
        else:
            should_send = True
    
    if should_send:
        email_service = EmailDigestService(db)
        days = 1 if prefs.digest_frequency == 'daily' else 7
        papers = db.get_papers_for_digest(since_days=days)
        
        if papers:
            success, msg = email_service.send_digest(prefs.email, papers, prefs.digest_frequency)
            print(f"[{datetime.now()}] {msg}")
        else:
            print(f"[{datetime.now()}] No new papers to send")
    else:
        print(f"[{datetime.now()}] Not time yet")


def run_scheduler():
    """Run the scheduler"""
    print("=" * 50)
    print("📧 Paper Digest Scheduler Started")
    print("=" * 50)
    
    # Check every hour
    schedule.every().hour.at(":00").do(check_and_send_digest)
    
    # Run once on start
    check_and_send_digest()
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()