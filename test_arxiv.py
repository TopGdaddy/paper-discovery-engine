"""
test_arxiv.py - Quick test to check if arXiv is accessible
Run this to see if the rate limit has been lifted!
"""

import urllib.request
import ssl
import certifi

def test_arxiv_connection():
    """Test if we can connect to arXiv API."""
    
    print("🧪 Testing arXiv connection...\n")
    
    # Simple test URL - just get 1 paper
    test_url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=1"
    
    try:
        # Create SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Create request with headers
        req = urllib.request.Request(
            test_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36'
            }
        )
        
        # Try to fetch
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            data = response.read().decode('utf-8')
        
        # Check if we got XML (good) or HTML error page (blocked)
        if '<?xml' in data or '<feed' in data:
            print("✅ SUCCESS! arXiv is responding normally!")
            print("   You can run your scraper now.\n")
            
            # Show a snippet
            if '<entry>' in data:
                print("📄 Sample data received:")
                # Extract title
                start = data.find('<title>') + 7
                end = data.find('</title>', start)
                if start > 7 and end > start:
                    title = data[start:end]
                    print(f"   First paper: {title[:60]}...")
            return True
            
        elif 'rate limit' in data.lower() or 'blocked' in data.lower():
            print("❌ STILL BLOCKED - arXiv is rate limiting you")
            print("   Wait another 10-15 minutes and try again.")
            return False
            
        else:
            print("⚠️  Got unexpected response. Might still be blocked.")
            print(f"   First 200 chars: {data[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_arxiv_connection()