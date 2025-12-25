"""
ml_engine.py - Machine Learning Engine for Paper Discovery
"""

import pickle
import base64
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class PaperMLEngine:
    """ML engine that learns from user behavior"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.model = None
        self.vectorizer = None
        self.is_trained = False
        self.metrics = {}
        self._load_model()
    
    def _load_model(self):
        """Load model from database if exists"""
        try:
            model_state = self.db.get_active_model()
            if model_state and model_state.model_blob:
                self.model = pickle.loads(base64.b64decode(model_state.model_blob))
                self.vectorizer = pickle.loads(base64.b64decode(model_state.vectorizer_blob))
                self.is_trained = True
                self.metrics = {
                    'accuracy': model_state.accuracy,
                    'trained_at': model_state.trained_at,
                    'samples': model_state.training_samples
                }
                return True
        except Exception as e:
            print(f"Could not load model: {e}")
        return False
    
    def _prepare_text(self, paper) -> str:
        """Prepare paper text for ML"""
        parts = []
        if paper.title:
            parts.append(paper.title)
        if paper.summary:
            parts.append(paper.summary)
        if paper.authors:
            parts.append(paper.authors)
        if paper.primary_category:
            parts.append(paper.primary_category)
        return ' '.join(parts)
    
    def get_training_data(self) -> Tuple[List[str], List[int]]:
        """Get labeled papers for training"""
        labeled_papers = self.db.get_labeled_papers()
        
        texts = []
        labels = []
        
        for paper in labeled_papers:
            text = self._prepare_text(paper)
            if text and paper.user_label is not None:
                texts.append(text)
                labels.append(paper.user_label)
        
        return texts, labels
    
    def train(self, min_samples=5) -> Dict:
        """Train the classifier on user's labeled papers"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        texts, labels = self.get_training_data()
        
        if len(texts) < min_samples:
            return {
                'success': False,
                'error': f'Need at least {min_samples} labeled papers. You have {len(texts)}.',
                'current_count': len(texts),
                'required_count': min_samples
            }
        
        unique_labels = set(labels)
        if len(unique_labels) < 2:
            return {
                'success': False,
                'error': 'Need both relevant and not-relevant examples!',
                'current_count': len(texts)
            }
        
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=1,
                max_df=0.95
            )
            
            X = self.vectorizer.fit_transform(texts)
            y = np.array(labels)
            
            self.model = LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                C=1.0,
                random_state=42
            )
            
            if len(texts) >= 10:
                cv_scores = cross_val_score(self.model, X, y, cv=min(5, len(texts)//2))
                cv_accuracy = cv_scores.mean()
            else:
                cv_accuracy = None
            
            self.model.fit(X, y)
            y_pred = self.model.predict(X)
            
            metrics = {
                'success': True,
                'samples': len(texts),
                'positive_samples': sum(labels),
                'negative_samples': len(labels) - sum(labels),
                'accuracy': accuracy_score(y, y_pred),
                'precision': precision_score(y, y_pred, zero_division=0),
                'recall': recall_score(y, y_pred, zero_division=0),
                'f1': f1_score(y, y_pred, zero_division=0),
                'cv_accuracy': cv_accuracy,
                'trained_at': datetime.utcnow()
            }
            
            feature_names = self.vectorizer.get_feature_names_out()
            coefficients = self.model.coef_[0]
            
            top_positive_idx = np.argsort(coefficients)[-10:][::-1]
            top_negative_idx = np.argsort(coefficients)[:10]
            
            metrics['top_positive'] = [
                {'word': feature_names[i], 'score': float(coefficients[i])}
                for i in top_positive_idx
            ]
            metrics['top_negative'] = [
                {'word': feature_names[i], 'score': float(coefficients[i])}
                for i in top_negative_idx
            ]
            
            model_blob = base64.b64encode(pickle.dumps(self.model)).decode('utf-8')
            vectorizer_blob = base64.b64encode(pickle.dumps(self.vectorizer)).decode('utf-8')
            self.db.save_model_state(model_blob, vectorizer_blob, metrics)
            
            self.is_trained = True
            self.metrics = metrics
            
            return metrics
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def predict_relevance(self, paper) -> Optional[float]:
        """Predict relevance score for a single paper"""
        if not self.is_trained or not self.model or not self.vectorizer:
            return None
        
        try:
            text = self._prepare_text(paper)
            X = self.vectorizer.transform([text])
            proba = self.model.predict_proba(X)[0]
            relevant_idx = list(self.model.classes_).index(1)
            return float(proba[relevant_idx])
        except:
            return None
    
    def score_all_papers(self, limit=1000) -> Dict[str, float]:
        """Score all papers and update database"""
        if not self.is_trained:
            return {}
        
        papers = self.db.get_all_papers(limit=limit)
        scores = {}
        
        for paper in papers:
            score = self.predict_relevance(paper)
            if score is not None:
                scores[paper.arxiv_id] = score
        
        self.db.update_user_scores(scores)
        return scores
    
    def get_recommendations(self, limit=10) -> List:
        """Get top recommended papers based on user's model"""
        if not self.is_trained:
            return self.db.get_all_papers(limit=limit)
        
        papers = self.db.get_all_papers(limit=500)
        scored_papers = []
        
        for paper in papers:
            if paper.user_label is not None:
                continue
            
            score = self.predict_relevance(paper)
            if score is not None:
                scored_papers.append((paper, score))
        
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        return [p for p, s in scored_papers[:limit]]