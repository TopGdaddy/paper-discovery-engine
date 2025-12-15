"""
file_handler.py - Save and load papers from files
Before we set up a database, let's save papers as JSON files.
"""
import json
import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path

class PaperFileHandler:
    """Handles saving and loading papers from the filesystem"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the file handler.
        Args:
            data_dir: Directory to store paper data
        """
        self.data_dir = Path(data_dir)
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)
        
    def save_papers(self, papers: List[Dict], filename: str = None) -> str:
        """
        Save papers to a JSON file.
        Returns: Path to the saved file
        """
        # Generate filename with timestamp if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"papers_{timestamp}.json"
            
        filepath = self.data_dir / filename
        
        # Convert datetime objects to strings for JSON (JSON hates dates)
        papers_serializable = []
        for paper in papers:
            paper_copy = paper.copy()
            if isinstance(paper_copy['published'], datetime):
                paper_copy['published'] = paper_copy['published'].isoformat()
            papers_serializable.append(paper_copy)
            
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(papers_serializable, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Saved {len(papers)} papers to: {filepath}")
        return str(filepath)
        
    def load_papers(self, filename: str) -> List[Dict]:
        """
        Load papers from a JSON file.
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return []
            
        with open(filepath, 'r', encoding='utf-8') as f:
            papers = json.load(f)
            
        print(f"📂 Loaded {len(papers)} papers from: {filepath}")
        return papers

    def list_saved_files(self) -> List[str]:
        """List all saved paper files"""
        # Use pathlib to find all .json files
        json_files = list(self.data_dir.glob("papers_*.json"))
        # Return names sorted by newest first
        return [f.name for f in sorted(json_files, reverse=True)]

# ---------------------------------------------------------
# 🧪 TEST BLOCK
# ---------------------------------------------------------
if __name__ == "__main__":
    # We need to import our Scraper to get some data to test with!
    # Note: This import works because scraper.py is in the same folder
    try:
        from scraper import ArXivScraper, print_paper_info
    except ImportError:
        # Fallback if running from root directory
        import sys
        sys.path.append('src')
        from scraper import ArXivScraper, print_paper_info

    print("🧪 Testing File Handler\n")
    
    # 1. Fetch some papers
    print("1. Fetching papers...")
    scraper = ArXivScraper(max_results=3)
    papers = scraper.get_latest_papers(category="cs.AI", count=3)
    
    # 2. Save them
    print("\n2. Saving papers...")
    handler = PaperFileHandler()
    saved_file_path = handler.save_papers(papers)
    
    # 3. List saved files
    print("\n3. Checking folder...")
    print("📋 Saved files:")
    for file in handler.list_saved_files():
        print(f"   - {file}")
        
    # 4. Load them back
    print("\n4. Loading papers back...")
    # Extract just the filename from the path
    filename_only = os.path.basename(saved_file_path)
    loaded_papers = handler.load_papers(filename_only)
    
    # 5. Verify
    print("\n✅ Verification - First loaded paper title:")
    if loaded_papers:
        print(f"   {loaded_papers[0]['title']}")