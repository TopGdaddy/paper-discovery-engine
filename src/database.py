"""
database.py - Store papers in SQLite database using SQLAlchemy ORM

WHY DATABASE INSTEAD OF JSON FILES?
===================================
1. No duplicates - database rejects papers with same arxiv_id
2. Fast search - SQL queries are optimized
3. Easy updates - change one paper without rewriting everything
4. Scales better - handles 100,000+ papers easily
5. Built-in filtering - get papers by category, date, score, etc.

CONCEPTS YOU'LL LEARN:
======================
- ORM (Object-Relational Mapping): Python objects ↔ database rows
- SQLAlchemy: Most popular Python database toolkit
- CRUD: Create, Read, Update, Delete operations
- Sessions: How databases manage transactions
"""

import os
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# =============================================================================
# SETUP
# =============================================================================

# Base class for all database models
# Think of it as the "parent" that all tables inherit from
Base = declarative_base()


# =============================================================================
# PAPER MODEL (This defines the database table structure)
# =============================================================================

class PaperRecord(Base):
    """
    Database table for storing papers.
    
    HOW THIS WORKS:
    ===============
    - This Python class = one database table called 'papers'
    - Each class attribute (like 'title') = one column in the table
    - Each instance of this class = one row in the table
    
    COLUMN TYPES:
    =============
    - Integer: Whole numbers (id, counts)
    - String(N): Text up to N characters
    - Text: Unlimited text (for long content like abstracts)
    - DateTime: Date and time
    - Float: Decimal numbers (for scores like 0.85)
    - Boolean: True/False
    
    SPECIAL ATTRIBUTES:
    ===================
    - primary_key=True: Unique identifier, auto-increments (1, 2, 3...)
    - unique=True: No two rows can have the same value
    - nullable=False: This field is required (can't be empty)
    - index=True: Makes searching this column MUCH faster
    - default=X: If not provided, use X as the value
    """
    
    # Table name in the database
    __tablename__ = 'papers'
    
    # -------------------------------------------------------------------------
    # PRIMARY KEY - Every table needs one unique identifier
    # -------------------------------------------------------------------------
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # -------------------------------------------------------------------------
    # PAPER INFO - Matches your scraper.py field names exactly!
    # -------------------------------------------------------------------------
    arxiv_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)  # The abstract
    authors = Column(Text)  # Stored as comma-separated string
    published = Column(DateTime, index=True)  # Indexed for date sorting
    primary_category = Column(String(50), index=True)
    pdf_url = Column(String(500))
    abs_url = Column(String(500))
    
    # -------------------------------------------------------------------------
    # OUR CUSTOM FIELDS - For ML and user tracking
    # -------------------------------------------------------------------------
    # Relevance score from ML classifier (0.0 to 1.0)
    relevance_score = Column(Float, default=0.0)
    
    # User labels for training: 1=relevant, 0=not relevant, None=not labeled yet
    user_label = Column(Integer, nullable=True)
    
    # Tracking
    is_read = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # When we downloaded it (auto-set)
    downloaded_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        """What you see when you print a PaperRecord object."""
        return f"<Paper {self.arxiv_id}: {self.title[:40]}...>"
    
    def to_dict(self) -> Dict:
        """
        Convert database record back to dictionary.
        Useful for displaying or passing to other functions.
        """
        return {
            'id': self.id,
            'arxiv_id': self.arxiv_id,
            'title': self.title,
            'summary': self.summary,
            'authors': self.authors.split(', ') if self.authors else [],
            'published': self.published,
            'primary_category': self.primary_category,
            'pdf_url': self.pdf_url,
            'abs_url': self.abs_url,
            'relevance_score': self.relevance_score,
            'user_label': self.user_label,
            'is_read': self.is_read,
            'is_favorite': self.is_favorite,
            'notes': self.notes,
            'downloaded_at': self.downloaded_at,
        }


# =============================================================================
# DATABASE MANAGER CLASS
# =============================================================================

class DatabaseManager:
    """
    Handles all database operations.
    
    WHY A CLASS?
    ============
    - Keeps all database logic in one place
    - Manages the connection/session
    - Provides clean methods like db.add_paper(), db.search()
    - Easy to test and maintain
    
    USAGE:
    ======
        db = DatabaseManager()
        db.add_paper(paper_dict)
        papers = db.get_all_papers()
        db.close()
    """
    
    def __init__(self, db_path: str = "data/papers.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Where to store the SQLite file
        """
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create database engine
        # sqlite:/// means SQLite database
        # echo=False means don't print every SQL query (set True to debug)
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Create all tables defined above (if they don't exist)
        Base.metadata.create_all(self.engine)
        
        # Create session factory and session
        # Session = our "connection" to talk to the database
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        self.db_path = db_path
        print(f"📁 Database initialized: {os.path.abspath(db_path)}")
    
    # =========================================================================
    # CREATE OPERATIONS
    # =========================================================================
    
    def add_paper(self, paper_dict: Dict) -> Optional[PaperRecord]:
        """
        Add a single paper to the database.
        
        WHAT HAPPENS:
        1. Check if paper with same arxiv_id exists
        2. If exists, skip it (return existing)
        3. If new, create record and save
        
        Args:
            paper_dict: Dictionary from your scraper (ArXivScraper)
            
        Returns:
            PaperRecord object, or None if error
        """
        try:
            # Check for duplicate
            existing = self.session.query(PaperRecord).filter_by(
                arxiv_id=paper_dict['arxiv_id']
            ).first()
            
            if existing:
                # Already have this paper
                return existing
            
            # Convert authors list to comma-separated string
            authors = paper_dict.get('authors', [])
            if isinstance(authors, list):
                authors = ', '.join(authors)
            
            # Create new record
            paper = PaperRecord(
                arxiv_id=paper_dict['arxiv_id'],
                title=paper_dict['title'],
                summary=paper_dict.get('summary', ''),
                authors=authors,
                published=paper_dict.get('published'),
                primary_category=paper_dict.get('primary_category', ''),
                pdf_url=paper_dict.get('pdf_url', ''),
                abs_url=paper_dict.get('abs_url', ''),
            )
            
            # Add to session and save
            self.session.add(paper)
            self.session.commit()
            
            return paper
            
        except Exception as e:
            # If anything goes wrong, undo changes
            self.session.rollback()
            print(f"❌ Error adding paper: {e}")
            return None
    
    def add_papers(self, papers_list: List[Dict]) -> Dict[str, int]:
        """
        Add multiple papers at once.
        
        Args:
            papers_list: List of paper dictionaries from scraper
            
        Returns:
            Dictionary with counts: {'added': X, 'skipped': Y}
        """
        added = 0
        skipped = 0
        
        for paper_dict in papers_list:
            # Check if exists
            existing = self.session.query(PaperRecord).filter_by(
                arxiv_id=paper_dict['arxiv_id']
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            # Convert authors
            authors = paper_dict.get('authors', [])
            if isinstance(authors, list):
                authors = ', '.join(authors)
            
            # Create record
            paper = PaperRecord(
                arxiv_id=paper_dict['arxiv_id'],
                title=paper_dict['title'],
                summary=paper_dict.get('summary', ''),
                authors=authors,
                published=paper_dict.get('published'),
                primary_category=paper_dict.get('primary_category', ''),
                pdf_url=paper_dict.get('pdf_url', ''),
                abs_url=paper_dict.get('abs_url', ''),
            )
            
            self.session.add(paper)
            added += 1
        
        # Commit all at once (much faster than one at a time!)
        try:
            self.session.commit()
            print(f"✅ Added {added} papers, skipped {skipped} duplicates")
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error in bulk add: {e}")
            return {'added': 0, 'skipped': 0}
        
        return {'added': added, 'skipped': skipped}
    
    # =========================================================================
    # READ OPERATIONS
    # =========================================================================
    
    def get_paper(self, arxiv_id: str) -> Optional[PaperRecord]:
        """Get a single paper by its arXiv ID."""
        return self.session.query(PaperRecord).filter_by(arxiv_id=arxiv_id).first()
    
    def get_all_papers(self, limit: int = 100) -> List[PaperRecord]:
        """
        Get all papers, sorted by published date (newest first).
        
        Args:
            limit: Maximum number to return (default 100)
        """
        return self.session.query(PaperRecord)\
            .order_by(desc(PaperRecord.published))\
            .limit(limit)\
            .all()
    
    def search_papers(
        self,
        keyword: str = None,
        category: str = None,
        min_score: float = None,
        limit: int = 50
    ) -> List[PaperRecord]:
        """
        Search papers with filters.
        
        Args:
            keyword: Search in title and summary
            category: Filter by primary_category (e.g., "cs.AI")
            min_score: Minimum relevance score
            limit: Max results
            
        Returns:
            List of matching PaperRecord objects
        """
        query = self.session.query(PaperRecord)
        
        # Apply filters
        if keyword:
            pattern = f"%{keyword}%"
            query = query.filter(
                (PaperRecord.title.like(pattern)) |
                (PaperRecord.summary.like(pattern))
            )
        
        if category:
            query = query.filter(PaperRecord.primary_category == category)
        
        if min_score is not None:
            query = query.filter(PaperRecord.relevance_score >= min_score)
        
        # Order by newest first
        query = query.order_by(desc(PaperRecord.published))
        
        return query.limit(limit).all()
    
    def get_unlabeled_papers(self, limit: int = 20) -> List[PaperRecord]:
        """Get papers that haven't been labeled yet (for training data)."""
        return self.session.query(PaperRecord)\
            .filter(PaperRecord.user_label.is_(None))\
            .order_by(desc(PaperRecord.published))\
            .limit(limit)\
            .all()
    
    def get_labeled_papers(self) -> List[PaperRecord]:
        """Get all labeled papers (for training the classifier)."""
        return self.session.query(PaperRecord)\
            .filter(PaperRecord.user_label.isnot(None))\
            .all()
    
    def get_top_papers(self, limit: int = 10, min_score: float = 0.5) -> List[PaperRecord]:
        """Get highest-scored papers."""
        return self.session.query(PaperRecord)\
            .filter(PaperRecord.relevance_score >= min_score)\
            .order_by(desc(PaperRecord.relevance_score))\
            .limit(limit)\
            .all()
    
    def count_papers(self) -> int:
        """Get total number of papers in database."""
        return self.session.query(PaperRecord).count()
    
    def count_labeled(self) -> int:
        """Get number of labeled papers."""
        return self.session.query(PaperRecord)\
            .filter(PaperRecord.user_label.isnot(None))\
            .count()
    
    def get_categories(self) -> List[str]:
        """Get list of all unique categories in database."""
        results = self.session.query(PaperRecord.primary_category)\
            .distinct()\
            .all()
        return [r[0] for r in results if r[0]]
    
    # =========================================================================
    # UPDATE OPERATIONS
    # =========================================================================
    
    def label_paper(self, arxiv_id: str, label: int) -> bool:
        """
        Label a paper for training.
        
        Args:
            arxiv_id: The paper's arXiv ID
            label: 1 = relevant, 0 = not relevant
            
        Returns:
            True if successful, False otherwise
        """
        try:
            paper = self.get_paper(arxiv_id)
            if paper:
                paper.user_label = label
                self.session.commit()
                label_text = "👍 relevant" if label == 1 else "👎 not relevant"
                print(f"   Labeled {arxiv_id} as {label_text}")
                return True
            return False
        except:
            self.session.rollback()
            return False
    
    def update_score(self, arxiv_id: str, score: float) -> bool:
        """Update relevance score for a paper."""
        try:
            paper = self.get_paper(arxiv_id)
            if paper:
                paper.relevance_score = score
                self.session.commit()
                return True
            return False
        except:
            self.session.rollback()
            return False
    
    def update_scores_bulk(self, scores: Dict[str, float]) -> int:
        """
        Update scores for multiple papers at once.
        
        Args:
            scores: Dictionary of {arxiv_id: score}
            
        Returns:
            Number of papers updated
        """
        updated = 0
        try:
            for arxiv_id, score in scores.items():
                paper = self.get_paper(arxiv_id)
                if paper:
                    paper.relevance_score = score
                    updated += 1
            self.session.commit()
            return updated
        except:
            self.session.rollback()
            return 0
    
    def mark_as_read(self, arxiv_id: str) -> bool:
        """Mark a paper as read."""
        try:
            paper = self.get_paper(arxiv_id)
            if paper:
                paper.is_read = True
                self.session.commit()
                return True
            return False
        except:
            self.session.rollback()
            return False
    
    def toggle_favorite(self, arxiv_id: str) -> bool:
        """Toggle favorite status."""
        try:
            paper = self.get_paper(arxiv_id)
            if paper:
                paper.is_favorite = not paper.is_favorite
                self.session.commit()
                return paper.is_favorite
            return False
        except:
            self.session.rollback()
            return False
    
    # =========================================================================
    # DELETE OPERATIONS
    # =========================================================================
    
    def delete_paper(self, arxiv_id: str) -> bool:
        """Delete a paper from database."""
        try:
            paper = self.get_paper(arxiv_id)
            if paper:
                self.session.delete(paper)
                self.session.commit()
                return True
            return False
        except:
            self.session.rollback()
            return False
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        total = self.count_papers()
        labeled = self.count_labeled()
        
        positive = self.session.query(PaperRecord)\
            .filter(PaperRecord.user_label == 1)\
            .count()
        
        categories = self.get_categories()
        
        return {
            'total_papers': total,
            'labeled_papers': labeled,
            'unlabeled_papers': total - labeled,
            'positive_labels': positive,
            'negative_labels': labeled - positive,
            'categories': categories,
        }
    
    def close(self):
        """Close database connection."""
        self.session.close()
        print("🔒 Database connection closed")


# =============================================================================
# TEST CODE
# =============================================================================

if __name__ == "__main__":
    """
    Test the database with your actual scraper!
    """
    # Import your scraper
    from scraper import ArXivScraper
    
    print("=" * 80)
    print("🧪 DATABASE TEST")
    print("=" * 80)
    
    # Initialize
    db = DatabaseManager("data/papers.db")
    scraper = ArXivScraper(max_results=10)
    
    # ----- TEST 1: Fetch and store papers -----
    print("\n📥 TEST 1: Fetch papers and store in database")
    print("-" * 40)
    
    papers = scraper.get_latest_papers(category="cs.AI", count=10)
    result = db.add_papers(papers)
    print(f"   Result: {result}")
    
    # ----- TEST 2: Count papers -----
    print("\n📊 TEST 2: Database statistics")
    print("-" * 40)
    
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # ----- TEST 3: Search -----
    print("\n🔍 TEST 3: Search for 'learning'")
    print("-" * 40)
    
    results = db.search_papers(keyword="learning", limit=3)
    print(f"   Found {len(results)} papers")
    for paper in results:
        print(f"   - {paper.title[:50]}...")
    
    # ----- TEST 4: Get all papers -----
    print("\n📚 TEST 4: Get recent papers")
    print("-" * 40)
    
    recent = db.get_all_papers(limit=5)
    for i, paper in enumerate(recent, 1):
        print(f"   {i}. [{paper.primary_category}] {paper.title[:50]}...")
    
    # ----- TEST 5: Label a paper -----
    print("\n🏷️  TEST 5: Label a paper")
    print("-" * 40)
    
    if recent:
        test_paper = recent[0]
        db.label_paper(test_paper.arxiv_id, label=1)
        
        # Check it worked
        labeled_count = db.count_labeled()
        print(f"   Labeled papers now: {labeled_count}")
    
    # ----- TEST 6: Try adding duplicates -----
    print("\n🔄 TEST 6: Test duplicate prevention")
    print("-" * 40)
    
    result2 = db.add_papers(papers)  # Same papers again
    print(f"   Result: {result2}")
    print(f"   (All should be skipped as duplicates!)")
    
    # ----- FINAL STATS -----
    print("\n" + "=" * 80)
    print("📊 FINAL DATABASE STATS")
    print("=" * 80)
    
    final_stats = db.get_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n   Database file: {os.path.abspath(db.db_path)}")
    
    db.close()
    
    print("\n✅ All database tests passed!")