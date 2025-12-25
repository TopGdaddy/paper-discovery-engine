"""
database.py - Enhanced Database with Full Auto-Migration
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

Base = declarative_base()


class PaperRecord(Base):
    """Research paper record"""
    __tablename__ = 'papers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    arxiv_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    authors = Column(Text)
    summary = Column(Text)
    pdf_url = Column(String(500))
    abs_url = Column(String(500))
    primary_category = Column(String(50), index=True)
    published = Column(DateTime, index=True)
    relevance_score = Column(Float, default=0.0, index=True)
    
    # New fields - will be migrated
    fetched_at = Column(DateTime, nullable=True)
    user_label = Column(Integer, nullable=True)
    labeled_at = Column(DateTime, nullable=True)
    is_saved = Column(Boolean, default=False)
    saved_at = Column(DateTime, nullable=True)
    user_score = Column(Float, nullable=True)
    
    def to_dict(self):
        return {
            'arxiv_id': self.arxiv_id,
            'title': self.title,
            'authors': self.authors,
            'summary': self.summary,
            'pdf_url': self.pdf_url,
            'abs_url': self.abs_url,
            'primary_category': self.primary_category,
            'published': self.published.isoformat() if self.published else None,
            'relevance_score': self.relevance_score,
            'user_label': self.user_label,
            'is_saved': self.is_saved,
            'user_score': self.user_score
        }


class UserPreferences(Base):
    """User preferences for email digest"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=True)
    email_verified = Column(Boolean, default=False)
    digest_enabled = Column(Boolean, default=False)
    digest_frequency = Column(String(20), default='weekly')
    digest_day = Column(Integer, default=0)
    digest_hour = Column(Integer, default=8)
    tracked_categories = Column(Text, default='[]')
    tracked_keywords = Column(Text, default='[]')
    min_relevance_score = Column(Float, default=0.5)
    max_papers_per_digest = Column(Integer, default=10)
    notify_high_relevance = Column(Boolean, default=True)
    auto_train = Column(Boolean, default=True)
    model_last_trained = Column(DateTime, nullable=True)
    model_accuracy = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    smtp_host = Column(String(255), default='smtp.gmail.com')
    smtp_port = Column(Integer, default=587)
    smtp_user = Column(String(255), nullable=True)
    smtp_password = Column(String(255), nullable=True)
    
    def get_tracked_categories(self):
        try:
            return json.loads(self.tracked_categories or '[]')
        except:
            return []
    
    def set_tracked_categories(self, categories):
        self.tracked_categories = json.dumps(categories)
    
    def get_tracked_keywords(self):
        try:
            return json.loads(self.tracked_keywords or '[]')
        except:
            return []
    
    def set_tracked_keywords(self, keywords):
        self.tracked_keywords = json.dumps(keywords)


class DigestHistory(Base):
    """Track sent digests"""
    __tablename__ = 'digest_history'
    
    id = Column(Integer, primary_key=True)
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    paper_ids = Column(Text)
    paper_count = Column(Integer)
    digest_type = Column(String(20))
    status = Column(String(20), default='sent')
    
    def get_paper_ids(self):
        try:
            return json.loads(self.paper_ids or '[]')
        except:
            return []


class MLModelState(Base):
    """Store ML model state"""
    __tablename__ = 'ml_model_state'
    
    id = Column(Integer, primary_key=True)
    model_type = Column(String(50), default='tfidf_logreg')
    model_blob = Column(Text)
    vectorizer_blob = Column(Text)
    trained_at = Column(DateTime)
    training_samples = Column(Integer)
    accuracy = Column(Float)
    precision_score = Column(Float)
    recall_score = Column(Float)
    f1_score = Column(Float)
    top_positive_features = Column(Text)
    top_negative_features = Column(Text)
    is_active = Column(Boolean, default=True)


class DatabaseManager:
    def __init__(self, db_path: str):
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # First migrate the papers table BEFORE creating models
        self._migrate_papers_table()
        
        # Now create all tables
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Ensure user preferences exist
        self._ensure_preferences()
    
    def _get_existing_columns(self, table_name):
        """Get list of existing columns in a table"""
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            return [col['name'] for col in columns]
        except:
            return []
    
    def _migrate_papers_table(self):
        """Add missing columns to existing papers table"""
        existing_cols = self._get_existing_columns('papers')
        
        if not existing_cols:
            # Table doesn't exist yet, will be created by create_all
            return
        
        # Columns to add if missing
        columns_to_add = {
            "fetched_at": "DATETIME",
            "user_label": "INTEGER",
            "labeled_at": "DATETIME",
            "is_saved": "INTEGER DEFAULT 0",
            "saved_at": "DATETIME",
            "user_score": "REAL",
        }
        
        with self.engine.connect() as conn:
            for col_name, col_type in columns_to_add.items():
                if col_name not in existing_cols:
                    try:
                        conn.execute(text(f"ALTER TABLE papers ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        print(f"✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"Column {col_name} might already exist: {e}")
    
    def _ensure_preferences(self):
        prefs = self.session.query(UserPreferences).first()
        if not prefs:
            prefs = UserPreferences()
            self.session.add(prefs)
            self.session.commit()
    
    # =========================================================================
    # PAPER OPERATIONS
    # =========================================================================
    
    def get_all_papers(self, limit=1000):
        return self.session.query(PaperRecord).order_by(
            PaperRecord.relevance_score.desc()
        ).limit(limit).all()
    
    def get_paper_by_id(self, arxiv_id: str):
        return self.session.query(PaperRecord).filter_by(arxiv_id=arxiv_id).first()
    
    def save_paper(self, paper: PaperRecord):
        existing = self.get_paper_by_id(paper.arxiv_id)
        if existing:
            return existing
        self.session.add(paper)
        self.session.commit()
        return paper
    
    def count_papers(self):
        return self.session.query(PaperRecord).count()
    
    def count_labeled(self):
        return self.session.query(PaperRecord).filter(
            PaperRecord.user_label.isnot(None)
        ).count()
    
    def search_papers(self, keyword: str, limit=50):
        keyword = f"%{keyword}%"
        return self.session.query(PaperRecord).filter(
            (PaperRecord.title.ilike(keyword)) | 
            (PaperRecord.summary.ilike(keyword)) |
            (PaperRecord.authors.ilike(keyword))
        ).order_by(PaperRecord.relevance_score.desc()).limit(limit).all()
    
    def get_categories(self):
        results = self.session.query(PaperRecord.primary_category).distinct().all()
        return [r[0] for r in results if r[0]]
    
    # =========================================================================
    # LABELING OPERATIONS
    # =========================================================================
    
    def label_paper(self, arxiv_id: str, label: int):
        paper = self.get_paper_by_id(arxiv_id)
        if paper:
            paper.user_label = label
            paper.labeled_at = datetime.utcnow()
            self.session.commit()
            return True
        return False
    
    def get_unlabeled_papers(self, limit=10):
        return self.session.query(PaperRecord).filter(
            PaperRecord.user_label.is_(None)
        ).order_by(PaperRecord.relevance_score.desc()).limit(limit).all()
    
    def get_labeled_papers(self):
        return self.session.query(PaperRecord).filter(
            PaperRecord.user_label.isnot(None)
        ).all()
    
    def get_positive_papers(self):
        return self.session.query(PaperRecord).filter(
            PaperRecord.user_label == 1
        ).all()
    
    def get_negative_papers(self):
        return self.session.query(PaperRecord).filter(
            PaperRecord.user_label == 0
        ).all()
    
    # =========================================================================
    # READING LIST OPERATIONS
    # =========================================================================
    
    def save_to_reading_list(self, arxiv_id: str):
        paper = self.get_paper_by_id(arxiv_id)
        if paper:
            paper.is_saved = True
            paper.saved_at = datetime.utcnow()
            if paper.user_label is None:
                paper.user_label = 1
                paper.labeled_at = datetime.utcnow()
            self.session.commit()
            return True
        return False
    
    def get_reading_list(self):
        return self.session.query(PaperRecord).filter(
            PaperRecord.is_saved == True
        ).order_by(PaperRecord.saved_at.desc()).all()
    
    def remove_from_reading_list(self, arxiv_id: str):
        paper = self.get_paper_by_id(arxiv_id)
        if paper:
            paper.is_saved = False
            self.session.commit()
            return True
        return False
    
    # =========================================================================
    # USER PREFERENCES
    # =========================================================================
    
    def get_preferences(self) -> UserPreferences:
        prefs = self.session.query(UserPreferences).first()
        if not prefs:
            prefs = UserPreferences()
            self.session.add(prefs)
            self.session.commit()
        return prefs
    
    def update_preferences(self, **kwargs):
        prefs = self.get_preferences()
        for key, value in kwargs.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        prefs.updated_at = datetime.utcnow()
        self.session.commit()
        return prefs
    
    # =========================================================================
    # INTEREST TRACKING
    # =========================================================================
    
    def get_user_interests(self):
        positive_papers = self.get_positive_papers()
        saved_papers = self.get_reading_list()
        
        all_relevant = positive_papers + [p for p in saved_papers if p not in positive_papers]
        
        if not all_relevant:
            return {'categories': {}, 'keywords': []}
        
        categories = {}
        for paper in all_relevant:
            cat = paper.primary_category or 'unknown'
            categories[cat] = categories.get(cat, 0) + 1
        
        from collections import Counter
        import re
        
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
                     'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
                     'those', 'using', 'based', 'via', 'new', 'novel', 'approach', 'method'}
        
        words = []
        for paper in all_relevant:
            if paper.title:
                title_words = re.findall(r'\b[a-z]{3,}\b', paper.title.lower())
                words.extend([w for w in title_words if w not in stopwords])
        
        keyword_counts = Counter(words).most_common(20)
        
        return {
            'categories': dict(sorted(categories.items(), key=lambda x: -x[1])),
            'keywords': [kw for kw, count in keyword_counts if count >= 2]
        }
    
    # =========================================================================
    # DIGEST OPERATIONS
    # =========================================================================
    
    def get_papers_for_digest(self, since_days=7):
        prefs = self.get_preferences()
        since_date = datetime.utcnow() - timedelta(days=since_days)
        
        sent_ids = set()
        recent_digests = self.session.query(DigestHistory).filter(
            DigestHistory.sent_at >= since_date
        ).all()
        for digest in recent_digests:
            sent_ids.update(digest.get_paper_ids())
        
        # Get papers - use published date since fetched_at might be null
        query = self.session.query(PaperRecord).filter(
            PaperRecord.relevance_score >= prefs.min_relevance_score
        )
        
        tracked_cats = prefs.get_tracked_categories()
        if tracked_cats:
            query = query.filter(PaperRecord.primary_category.in_(tracked_cats))
        
        papers = query.order_by(PaperRecord.relevance_score.desc()).limit(50).all()
        papers = [p for p in papers if p.arxiv_id not in sent_ids]
        
        return papers[:prefs.max_papers_per_digest]
    
    def record_digest(self, paper_ids: list, digest_type: str, status='sent'):
        digest = DigestHistory(
            paper_ids=json.dumps(paper_ids),
            paper_count=len(paper_ids),
            digest_type=digest_type,
            status=status
        )
        self.session.add(digest)
        self.session.commit()
        return digest
    
    def get_digest_history(self, limit=10):
        return self.session.query(DigestHistory).order_by(
            DigestHistory.sent_at.desc()
        ).limit(limit).all()
    
    # =========================================================================
    # ML MODEL OPERATIONS
    # =========================================================================
    
    def save_model_state(self, model_blob: str, vectorizer_blob: str, metrics: dict):
        self.session.query(MLModelState).update({'is_active': False})
        
        state = MLModelState(
            model_blob=model_blob,
            vectorizer_blob=vectorizer_blob,
            trained_at=datetime.utcnow(),
            training_samples=metrics.get('samples', 0),
            accuracy=metrics.get('accuracy'),
            precision_score=metrics.get('precision'),
            recall_score=metrics.get('recall'),
            f1_score=metrics.get('f1'),
            top_positive_features=json.dumps(metrics.get('top_positive', [])),
            top_negative_features=json.dumps(metrics.get('top_negative', [])),
            is_active=True
        )
        self.session.add(state)
        self.session.commit()
        
        prefs = self.get_preferences()
        prefs.model_last_trained = datetime.utcnow()
        prefs.model_accuracy = metrics.get('accuracy')
        self.session.commit()
        
        return state
    
    def get_active_model(self):
        return self.session.query(MLModelState).filter_by(is_active=True).first()
    
    def update_user_scores(self, scores: dict):
        for arxiv_id, score in scores.items():
            paper = self.get_paper_by_id(arxiv_id)
            if paper:
                paper.user_score = score
        self.session.commit()
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self):
        total = self.session.query(PaperRecord).count()
        labeled = self.session.query(PaperRecord).filter(
            PaperRecord.user_label.isnot(None)
        ).count()
        positive = self.session.query(PaperRecord).filter(
            PaperRecord.user_label == 1
        ).count()
        negative = self.session.query(PaperRecord).filter(
            PaperRecord.user_label == 0
        ).count()
        saved = self.session.query(PaperRecord).filter(
            PaperRecord.is_saved == True
        ).count()
        
        return {
            'total_papers': total,
            'labeled_papers': labeled,
            'unlabeled_papers': total - labeled,
            'positive_labels': positive,
            'negative_labels': negative,
            'saved_papers': saved
        }