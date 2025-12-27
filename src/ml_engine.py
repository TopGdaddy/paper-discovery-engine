"""
ml_engine.py - Machine Learning Engine for Paper Discovery
Improved version with proper train/test evaluation
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
        """Train the classifier on user's labeled papers with proper evaluation"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split, LeaveOneOut, cross_val_score, cross_val_predict
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        texts, labels = self.get_training_data()
        
        # Check minimum samples
        if len(texts) < min_samples:
            return {
                'success': False,
                'error': f'Need at least {min_samples} labeled papers. You have {len(texts)}.',
                'current_count': len(texts),
                'required_count': min_samples
            }
        
        # Check for both classes
        unique_labels = set(labels)
        if len(unique_labels) < 2:
            return {
                'success': False,
                'error': 'Need both relevant and not-relevant examples!',
                'current_count': len(texts)
            }
        
        try:
            # Initialize vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=1,
                max_df=0.95
            )
            
            X = self.vectorizer.fit_transform(texts)
            y = np.array(labels)
            
            # Initialize model
            self.model = LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                C=1.0,
                random_state=42
            )
            
            n_samples = len(texts)
            n_positive = sum(labels)
            n_negative = len(labels) - sum(labels)
            
            # ================================================================
            # PROPER EVALUATION BASED ON SAMPLE SIZE
            # ================================================================
            
            if n_samples >= 20 and n_positive >= 4 and n_negative >= 4:
                # ----------------------------------------------------------
                # CASE 1: Enough samples for proper train/test split (20+)
                # ----------------------------------------------------------
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, 
                    test_size=0.2, 
                    random_state=42,
                    stratify=y
                )
                
                # Train on training set
                self.model.fit(X_train, y_train)
                
                # Evaluate on held-out test set
                y_pred_test = self.model.predict(X_test)
                
                test_accuracy = accuracy_score(y_test, y_pred_test)
                test_precision = precision_score(y_test, y_pred_test, zero_division=0)
                test_recall = recall_score(y_test, y_pred_test, zero_division=0)
                test_f1 = f1_score(y_test, y_pred_test, zero_division=0)
                
                # Cross-validation for additional robustness
                cv_folds = min(5, n_samples // 4)
                if cv_folds >= 2:
                    cv_scores = cross_val_score(self.model, X, y, cv=cv_folds)
                    cv_accuracy = cv_scores.mean()
                else:
                    cv_accuracy = test_accuracy
                
                evaluation_method = "train_test_split"
                
                # Retrain on ALL data for production use
                self.model.fit(X, y)
                
            elif n_samples >= 10:
                # ----------------------------------------------------------
                # CASE 2: Medium samples - use Leave-One-Out (10-19)
                # ----------------------------------------------------------
                # Leave-One-Out tests each sample individually
                loo = LeaveOneOut()
                y_pred_loo = cross_val_predict(self.model, X, y, cv=loo)
                
                test_accuracy = accuracy_score(y, y_pred_loo)
                test_precision = precision_score(y, y_pred_loo, zero_division=0)
                test_recall = recall_score(y, y_pred_loo, zero_division=0)
                test_f1 = f1_score(y, y_pred_loo, zero_division=0)
                cv_accuracy = test_accuracy  # LOO is a form of CV
                
                evaluation_method = "leave_one_out"
                
                # Train on all data for production
                self.model.fit(X, y)
                
            else:
                # ----------------------------------------------------------
                # CASE 3: Few samples - use k-fold cross-validation (5-9)
                # ----------------------------------------------------------
                cv_folds = max(2, min(n_samples, 5))
                
                try:
                    y_pred_cv = cross_val_predict(self.model, X, y, cv=cv_folds)
                    
                    test_accuracy = accuracy_score(y, y_pred_cv)
                    test_precision = precision_score(y, y_pred_cv, zero_division=0)
                    test_recall = recall_score(y, y_pred_cv, zero_division=0)
                    test_f1 = f1_score(y, y_pred_cv, zero_division=0)
                except:
                    # If cross-val fails, fall back to simple estimate
                    test_accuracy = 0.5  # Random chance
                    test_precision = 0.5
                    test_recall = 0.5
                    test_f1 = 0.5
                
                cv_accuracy = test_accuracy
                evaluation_method = "cross_val_predict"
                
                # Train on all data
                self.model.fit(X, y)
            
            # ================================================================
            # TRAINING SET METRICS (for reference only)
            # ================================================================
            y_pred_train = self.model.predict(X)
            training_accuracy = accuracy_score(y, y_pred_train)
            
            # ================================================================
            # RELIABILITY ASSESSMENT
            # ================================================================
            # Model is reliable if we have enough diverse samples
            is_reliable = (
                n_samples >= 20 and 
                n_positive >= 5 and 
                n_negative >= 5
            )
            
            # Confidence level
            if n_samples >= 50 and n_positive >= 15 and n_negative >= 15:
                confidence_level = "high"
            elif n_samples >= 20 and n_positive >= 5 and n_negative >= 5:
                confidence_level = "medium"
            else:
                confidence_level = "low"
            
            # ================================================================
            # EXTRACT FEATURE IMPORTANCE
            # ================================================================
            feature_names = self.vectorizer.get_feature_names_out()
            coefficients = self.model.coef_[0]
            
            top_positive_idx = np.argsort(coefficients)[-10:][::-1]
            top_negative_idx = np.argsort(coefficients)[:10]
            
            top_positive = [
                {'word': feature_names[i], 'score': float(coefficients[i])}
                for i in top_positive_idx
            ]
            top_negative = [
                {'word': feature_names[i], 'score': float(coefficients[i])}
                for i in top_negative_idx
            ]
            
            # ================================================================
            # BUILD METRICS DICT
            # ================================================================
            metrics = {
                'success': True,
                'samples': n_samples,
                'positive_samples': n_positive,
                'negative_samples': n_negative,
                'accuracy': test_accuracy,
                'precision': test_precision,
                'recall': test_recall,
                'f1': test_f1,
                'cv_accuracy': cv_accuracy,
                'training_accuracy': training_accuracy,
                'evaluation_method': evaluation_method,
                'is_reliable': is_reliable,
                'confidence_level': confidence_level,
                'top_positive': top_positive,
                'top_negative': top_negative,
                'trained_at': datetime.utcnow()
            }
            
            # ================================================================
            # SAVE MODEL TO DATABASE
            # ================================================================
            model_blob = base64.b64encode(pickle.dumps(self.model)).decode('utf-8')
            vectorizer_blob = base64.b64encode(pickle.dumps(self.vectorizer)).decode('utf-8')
            self.db.save_model_state(model_blob, vectorizer_blob, metrics)
            
            self.is_trained = True
            self.metrics = metrics
            
            return metrics
            
        except Exception as e:
            import traceback
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def predict_relevance(self, paper) -> Optional[float]:
        """Predict relevance score for a single paper"""
        if not self.is_trained or not self.model or not self.vectorizer:
            return None
        
        try:
            text = self._prepare_text(paper)
            X = self.vectorizer.transform([text])
            proba = self.model.predict_proba(X)[0]
            
            # Get index of the "relevant" class (label = 1)
            classes = list(self.model.classes_)
            if 1 in classes:
                relevant_idx = classes.index(1)
            else:
                relevant_idx = 0
                
            return float(proba[relevant_idx])
        except Exception as e:
            print(f"Prediction error: {e}")
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
        
        # Update scores in database
        self.db.update_user_scores(scores)
        return scores
    
    def get_recommendations(self, limit=10) -> List:
        """Get top recommended papers based on user's model"""
        if not self.is_trained:
            # Return random papers if not trained
            return self.db.get_all_papers(limit=limit)
        
        # Get unlabeled papers
        papers = self.db.get_all_papers(limit=500)
        scored_papers = []
        
        for paper in papers:
            # Skip already labeled papers
            if paper.user_label is not None:
                continue
            
            score = self.predict_relevance(paper)
            if score is not None:
                scored_papers.append((paper, score))
        
        # Sort by predicted relevance (highest first)
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        
        # Return top papers
        return [p for p, s in scored_papers[:limit]]
    
    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        if not self.is_trained:
            return {
                'is_trained': False,
                'message': 'No model trained yet'
            }
        
        return {
            'is_trained': True,
            'accuracy': self.metrics.get('accuracy'),
            'samples': self.metrics.get('samples'),
            'trained_at': self.metrics.get('trained_at'),
            'is_reliable': self.metrics.get('is_reliable', False),
            'confidence_level': self.metrics.get('confidence_level', 'unknown')
        }
