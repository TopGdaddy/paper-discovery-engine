"""
scraper.py - Downloads research papers from arXiv
Fixed: URL encoding AND SSL Certificate handling (Corrected for macOS)
"""

import feedparser
import time
import urllib.parse
import ssl
import certifi
from datetime import datetime
from typing import List, Dict, Optional

# -------------------------------------------------------------------------
# 🔧 THE CORRECT MAC SSL FIX
# We define a function that returns the secure context using certifi.
# -------------------------------------------------------------------------
def create_secure_context():
    return ssl.create_default_context(cafile=certifi.where())

# We tell Python: "When you need an HTTPS context, run this function."
ssl._create_default_https_context = create_secure_context

# arXiv API endpoint
ARXIV_API_URL = "http://export.arxiv.org/api/query"

class ArXivScraper:
    """
    A class to interact with arXiv's API and download paper information.
    """
    
    def __init__(self, max_results: int = 10):
        self.max_results = max_results
        self.api_url = ARXIV_API_URL
        
    def search_papers(
        self, 
        category: str = "cs.AI", 
        search_query: Optional[str] = None, 
        max_results: Optional[int] = None
    ) -> List[Dict]:
        
        # Use override if provided, otherwise use default
        results_limit = max_results if max_results else self.max_results
        
        # 1. Construct the raw query string
        if not search_query:
            raw_query = f'cat:{category}'
        else:
            raw_query = f'cat:{category} AND all:{search_query}'

        # 2. ENCODE THE QUERY
        encoded_query = urllib.parse.quote(raw_query)

        # 3. Build the parameters
        params = f"search_query={encoded_query}&start=0&max_results={results_limit}&sortBy=submittedDate&sortOrder=descending"
        
        # 4. Final URL
        query_url = f"{self.api_url}?{params}"
        
        print(f"🔍 Searching arXiv for {category}...")
        print(f"   Query: {raw_query}")
        
        try:
            # Make the API request
            feed = feedparser.parse(query_url)
            
            # Check for "bozo" bit (malformed feed)
            if feed.bozo:
                print(f"⚠️  Warning: Potential feed error: {feed.bozo_exception}")

            if not feed.entries:
                print("⚠️  No papers found!")
                return []
            
            print(f"✅ Found {len(feed.entries)} papers!\n")
            
            papers = []
            for entry in feed.entries:
                paper = self._extract_paper_info(entry)
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"❌ Error fetching papers: {e}")
            return []
    
    def _extract_paper_info(self, entry) -> Dict:
        """Extract relevant information from an arXiv entry."""
        # arXiv ID is in the URL
        arxiv_id = entry.id.split('/abs/')[-1]
        
        # Extract authors
        authors = [author.name for author in entry.authors]
        
        # Parse Date
        try:
            published_date = datetime.strptime(
                entry.published, 
                '%Y-%m-%dT%H:%M:%SZ'
            )
        except:
            published_date = entry.published
        
        # Get category
        primary_category = entry.tags[0]['term'] if entry.tags else 'unknown'
        
        # Clean summary
        summary = entry.summary.replace('\n', ' ').strip()
        
        return {
            'arxiv_id': arxiv_id,
            'title': entry.title,
            'authors': authors,
            'summary': summary,
            'published': published_date,
            'primary_category': primary_category,
            'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            'abs_url': f"https://arxiv.org/abs/{arxiv_id}"
        }
    
    def get_latest_papers(self, category: str = "cs.AI", count: int = 10) -> List[Dict]:
        print(f"📥 Fetching {count} latest papers from {category}...")
        return self.search_papers(category=category, max_results=count)
    
    def search_by_keywords(self, keywords: str, category: str = "cs.AI", count: int = 10) -> List[Dict]:
        print(f"🔎 Searching for '{keywords}' in {category}...")
        return self.search_papers(
            category=category,
            search_query=keywords,
            max_results=count
        )

def print_paper_info(paper: Dict) -> None:
    """Pretty print paper information."""
    print("=" * 80)
    print(f"📄 Title: {paper['title']}")
    print(f"🆔 arXiv ID: {paper['arxiv_id']}")
    print(f"📅 Published: {paper['published']}")
    print(f"🔗 PDF: {paper['pdf_url']}")
    print("=" * 80)
    print()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("🚀 arXiv Scraper Test\n")
    
    scraper = ArXivScraper(max_results=5)
    
    # Test 1
    print("\n" + "="*80)
    print("TEST 1: Latest AI Papers")
    print("="*80 + "\n")
    papers = scraper.get_latest_papers(category="cs.AI", count=5)
    if papers:
        for i, paper in enumerate(papers, 1):
            print_paper_info(paper)

    # Test 2
    print("\n" + "="*80)
    print("TEST 2: Search for 'large language models'")
    print("="*80 + "\n")
    
    time.sleep(1) # Be polite
    
    papers = scraper.search_by_keywords(
        keywords="large language models",
        category="cs.CL",
        count=3
    )
    if papers:
        for i, paper in enumerate(papers, 1):
            print_paper_info(paper)
    
    print("\n✅ Scraper test complete!")