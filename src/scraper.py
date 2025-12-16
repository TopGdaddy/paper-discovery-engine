"""
scraper.py - Downloads research papers from arXiv
VERSION 2.0: With proper rate limiting to prevent blocks!
"""

import feedparser
import time
import urllib.parse
import urllib.request
import ssl
import certifi
from datetime import datetime
from typing import List, Dict, Optional


# =============================================================================
# SSL FIX FOR MACOS
# =============================================================================
def create_secure_context():
    return ssl.create_default_context(cafile=certifi.where())

ssl._create_default_https_context = create_secure_context


# =============================================================================
# CONFIGURATION
# =============================================================================
ARXIV_API_URL = "http://export.arxiv.org/api/query"

# Rate limiting settings
MIN_DELAY_BETWEEN_REQUESTS = 3.0  # Minimum 3 seconds between requests
REQUESTS_BEFORE_LONG_PAUSE = 5     # After 5 requests, take a longer break
LONG_PAUSE_DURATION = 10.0         # 10 second pause after every 5 requests


# =============================================================================
# SCRAPER CLASS
# =============================================================================
class ArXivScraper:
    """
    A class to interact with arXiv's API with proper rate limiting.
    
    RATE LIMITING STRATEGY:
    - Wait at least 3 seconds between requests
    - After every 5 requests, wait 10 seconds
    - This prevents getting blocked by arXiv
    """
    
    def __init__(self, max_results: int = 10):
        self.max_results = max_results
        self.api_url = ARXIV_API_URL
        
        # Rate limiting tracking
        self._last_request_time = None
        self._request_count = 0
        
        # User agent to identify ourselves
        self._user_agent = 'PaperDiscoveryEngine/2.0 (Educational Project; Python/3.11)'
    
    def _wait_for_rate_limit(self):
        """
        Wait if necessary to respect rate limits.
        This is the KEY to not getting blocked!
        """
        # Check if we need a long pause
        if self._request_count > 0 and self._request_count % REQUESTS_BEFORE_LONG_PAUSE == 0:
            print(f"   ⏳ Taking a {LONG_PAUSE_DURATION}s break after {self._request_count} requests...")
            time.sleep(LONG_PAUSE_DURATION)
        
        # Always wait minimum delay since last request
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < MIN_DELAY_BETWEEN_REQUESTS:
                wait_time = MIN_DELAY_BETWEEN_REQUESTS - elapsed
                time.sleep(wait_time)
        
        # Update tracking
        self._last_request_time = time.time()
        self._request_count += 1
    
    def _fetch_url(self, url: str) -> Optional[bytes]:
        """
        Fetch URL with proper headers and error handling.
        Returns raw bytes or None if failed.
        """
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': self._user_agent,
                    'Accept': 'application/atom+xml',
                }
            )
            
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                return response.read()
                
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"   ❌ Rate limited (HTTP 429)! Wait 15+ minutes.")
            else:
                print(f"   ❌ HTTP Error {e.code}: {e.reason}")
            return None
            
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
            return None
    
    def _check_for_block(self, data: bytes) -> bool:
        """
        Check if the response indicates we're blocked.
        Returns True if blocked, False if OK.
        """
        try:
            text = data.decode('utf-8', errors='ignore')
            
            # Signs of being blocked
            if '<!DOCTYPE html' in text.lower():
                return True
            if 'rate limit' in text.lower():
                return True
            if '<feed' not in text and '<?xml' not in text:
                return True
                
            return False
            
        except:
            return True
    
    def search_papers(
        self, 
        category: str = "cs.AI", 
        search_query: Optional[str] = None, 
        max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for papers on arXiv.
        
        Args:
            category: arXiv category (e.g., "cs.AI", "cs.LG")
            search_query: Optional search terms
            max_results: Max papers to return
            
        Returns:
            List of paper dictionaries
        """
        results_limit = max_results if max_results else self.max_results
        
        # Build query
        if not search_query:
            raw_query = f'cat:{category}'
        else:
            raw_query = f'cat:{category} AND all:{search_query}'
        
        encoded_query = urllib.parse.quote(raw_query)
        params = f"search_query={encoded_query}&start=0&max_results={results_limit}&sortBy=submittedDate&sortOrder=descending"
        query_url = f"{self.api_url}?{params}"
        
        print(f"🔍 Searching arXiv for {category}...")
        print(f"   Query: {raw_query}")
        
        # Wait for rate limit
        self._wait_for_rate_limit()
        
        # Fetch data
        data = self._fetch_url(query_url)
        
        if data is None:
            return []
        
        # Check for block
        if self._check_for_block(data):
            print("   ❌ Appears to be blocked by arXiv. Wait 15+ minutes.")
            return []
        
        # Parse with feedparser
        try:
            feed = feedparser.parse(data)
            
            if feed.bozo and not feed.entries:
                print(f"   ⚠️ Feed parse error: {feed.bozo_exception}")
                return []
            
            if not feed.entries:
                print("   ⚠️ No papers found!")
                return []
            
            print(f"   ✅ Found {len(feed.entries)} papers!")
            
            papers = []
            for entry in feed.entries:
                try:
                    paper = self._extract_paper_info(entry)
                    papers.append(paper)
                except Exception as e:
                    print(f"   ⚠️ Skipped one paper (parse error): {e}")
            
            return papers
            
        except Exception as e:
            print(f"   ❌ Error parsing feed: {e}")
            return []
    
    def _extract_paper_info(self, entry) -> Dict:
        """Extract paper information from a feed entry."""
        # arXiv ID
        arxiv_id = entry.id.split('/abs/')[-1]
        
        # Authors
        authors = [author.name for author in getattr(entry, 'authors', [])]
        
        # Published date
        try:
            published_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')
        except:
            published_date = datetime.now()
        
        # Category
        primary_category = entry.tags[0]['term'] if getattr(entry, 'tags', []) else 'unknown'
        
        # Summary (clean up whitespace)
        summary = getattr(entry, 'summary', '')
        summary = ' '.join(summary.split())
        
        return {
            'arxiv_id': arxiv_id,
            'title': entry.title.replace('\n', ' ').strip(),
            'authors': authors,
            'summary': summary,
            'published': published_date,
            'primary_category': primary_category,
            'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            'abs_url': f"https://arxiv.org/abs/{arxiv_id}"
        }
    
    def get_latest_papers(self, category: str = "cs.AI", count: int = 10) -> List[Dict]:
        """Get latest papers from a category."""
        print(f"📥 Fetching {count} latest papers from {category}...")
        return self.search_papers(category=category, max_results=count)
    
    def search_by_keywords(self, keywords: str, category: str = "cs.AI", count: int = 10) -> List[Dict]:
        """Search for papers by keywords."""
        print(f"🔎 Searching for '{keywords}' in {category}...")
        return self.search_papers(category=category, search_query=keywords, max_results=count)
    
    def get_request_count(self) -> int:
        """Get the number of requests made so far."""
        return self._request_count


def print_paper_info(paper: Dict) -> None:
    """Pretty print paper information."""
    print("=" * 80)
    print(f"📄 Title: {paper['title']}")
    print(f"🆔 arXiv ID: {paper['arxiv_id']}")
    print(f"📅 Published: {paper['published']}")
    print(f"🔗 PDF: {paper['pdf_url']}")
    print("=" * 80)
    print()


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    print("🚀 arXiv Scraper Test (with rate limiting)\n")
    
    scraper = ArXivScraper(max_results=5)
    
    # Test 1: Latest AI Papers
    print("\n" + "=" * 80)
    print("TEST 1: Latest AI Papers")
    print("=" * 80 + "\n")
    
    papers = scraper.get_latest_papers(category="cs.AI", count=3)
    
    if papers:
        for paper in papers:
            print_paper_info(paper)
        print(f"✅ Test 1 passed! Got {len(papers)} papers.")
    else:
        print("❌ Test 1 failed - no papers returned.")
        print("   If you see 'blocked', wait 15 minutes and try again.")
    
    print(f"\n📊 Total requests made: {scraper.get_request_count()}")
    print("✅ Scraper test complete!")