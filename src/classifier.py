"""
classifier.py - ML Classifier to score paper relevance

HOW IT WORKS:
=============
1. You label some papers as relevant (1) or not relevant (0)
2. We convert paper text to numbers (embeddings)
3. We train a classifier on your labels
4. The classifier predicts scores for new papers!

CONCEPTS YOU'LL LEARN:
======================
- Text Embeddings: Converting text to numerical vectors
- Logistic Regression: Simple but effective classifier
- Train/Predict workflow: How ML models learn and make predictions
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# We'll import these after checking if they're installed
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML libraries not installed. Run: pip install scikit-learn sentence-transformers numpy")


# =============================================================================
# CONFIGURATION
# =============================================================================

# Model to use for text embeddings
# 'all-MiniLM-L6-v2' is small (80MB) and fast, good for starting
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

# Where to save trained models
MODEL_DIR = 'models'
CLASSIFIER_FILE = 'classifier.pkl'
EMBEDDER_CACHE = 'embedder_cache.pkl'


# =============================================================================
# PAPER CLASSIFIER CLASS
# =============================================================================

class PaperClassifier:
    """
    Classifies papers as relevant or not relevant based on your labels.
    
    WORKFLOW:
    =========
    1. Initialize: classifier = PaperClassifier()
    2. Train: classifier.train(labeled_papers)
    3. Predict: scores = classifier.predict(new_papers)
    4. Save: classifier.save()
    5. Load: classifier.load()
    
    HOW EMBEDDINGS WORK:
    ====================
    Text: "Deep learning for natural language processing"
           ↓
    Embedding Model (Sentence Transformer)
           ↓
    Vector: [0.23, -0.45, 0.12, ..., 0.89]  (384 numbers!)
    
    Similar papers have similar vectors!
    The classifier learns which vectors YOU find relevant.
    """
    
    def __init__(self):
        """Initialize the classifier."""
        
        if not ML_AVAILABLE:
            raise ImportError("ML libraries not installed. Run: pip install scikit-learn sentence-transformers numpy")
        
        # Create models directory
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        # Load embedding model (converts text to vectors)
        print(f"🔧 Loading embedding model: {EMBEDDING_MODEL}")
        print("   (This may take a minute on first run...)")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        print("   ✅ Embedding model loaded!")
        
        # Classifier (will be trained later)
        self.classifier = None
        self.is_trained = False
        
        # Stats
        self.training_accuracy = 0.0
        self.num_training_samples = 0
    
    def _get_paper_text(self, paper: Dict) -> str:
        """
        Combine paper fields into one text for embedding.
        
        We use title + summary because:
        - Title captures the main topic
        - Summary provides context and details
        - Together they give a complete picture
        """
        title = paper.get('title', '')
        summary = paper.get('summary', '')
        
        # Combine with a separator
        return f"{title}. {summary}"
    
    def _embed_papers(self, papers: List[Dict]) -> np.ndarray:
        """
        Convert papers to embedding vectors.
        
        Input: List of paper dicts
        Output: numpy array of shape (num_papers, 384)
        
        Each paper becomes a vector of 384 numbers!
        """
        texts = [self._get_paper_text(p) for p in papers]
        
        print(f"   📊 Embedding {len(texts)} papers...")
        embeddings = self.embedder.encode(texts, show_progress_bar=len(texts) > 10)
        
        return embeddings
    
    def train(self, labeled_papers: List[Dict], test_size: float = 0.2) -> Dict:
        """
        Train the classifier on labeled papers.
        
        Args:
            labeled_papers: List of paper dicts with 'user_label' field (0 or 1)
            test_size: Fraction of data to use for testing (default 20%)
            
        Returns:
            Dictionary with training results
            
        MINIMUM REQUIREMENTS:
        - At least 5 labeled papers
        - At least 2 positive (relevant) examples
        - At least 2 negative (not relevant) examples
        """
        print("\n🎓 TRAINING CLASSIFIER")
        print("=" * 50)
        
        # Validate input
        if len(labeled_papers) < 5:
            return {
                'success': False,
                'error': f'Need at least 5 labeled papers, got {len(labeled_papers)}'
            }
        
        # Extract labels
        labels = []
        valid_papers = []
        
        for paper in labeled_papers:
            label = paper.get('user_label')
            if label is not None:
                labels.append(int(label))
                valid_papers.append(paper)
        
        if len(valid_papers) < 5:
            return {
                'success': False,
                'error': f'Need at least 5 labeled papers, got {len(valid_papers)}'
            }
        
        # Check class balance
        num_positive = sum(labels)
        num_negative = len(labels) - num_positive
        
        print(f"   📊 Training data:")
        print(f"      👍 Relevant: {num_positive}")
        print(f"      👎 Not relevant: {num_negative}")
        print(f"      📝 Total: {len(labels)}")
        
        if num_positive < 2 or num_negative < 2:
            return {
                'success': False,
                'error': 'Need at least 2 examples of each class (relevant and not relevant)'
            }
        
        # Create embeddings
        print(f"\n   🔢 Creating embeddings...")
        X = self._embed_papers(valid_papers)
        y = np.array(labels)
        
        # Split into train/test sets
        if len(valid_papers) >= 10:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
        else:
            # Not enough data to split, use all for training
            X_train, X_test = X, X
            y_train, y_test = y, y
            print("   ⚠️  Small dataset - using all data for training")
        
        # Train classifier
        print(f"\n   🧠 Training Logistic Regression...")
        self.classifier = LogisticRegression(
            max_iter=1000,
            class_weight='balanced'  # Handle imbalanced classes
        )
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.is_trained = True
        self.training_accuracy = accuracy
        self.num_training_samples = len(valid_papers)
        
        print(f"\n   ✅ Training complete!")
        print(f"      🎯 Accuracy: {accuracy:.1%}")
        
        return {
            'success': True,
            'accuracy': accuracy,
            'num_samples': len(valid_papers),
            'num_positive': num_positive,
            'num_negative': num_negative,
        }
    
    def predict(self, papers: List[Dict]) -> List[float]:
        """
        Predict relevance scores for papers.
        
        Args:
            papers: List of paper dicts
            
        Returns:
            List of scores (0.0 to 1.0)
            Higher score = more likely to be relevant
        """
        if not self.is_trained:
            print("⚠️  Classifier not trained! Returning default scores.")
            return [0.5] * len(papers)
        
        if not papers:
            return []
        
        # Create embeddings
        X = self._embed_papers(papers)
        
        # Get probability of being relevant (class 1)
        probabilities = self.classifier.predict_proba(X)
        
        # Return probability of positive class
        scores = probabilities[:, 1].tolist()
        
        return scores
    
    def predict_single(self, paper: Dict) -> float:
        """Predict score for a single paper."""
        scores = self.predict([paper])
        return scores[0] if scores else 0.5
    
    def save(self, filepath: str = None) -> bool:
        """
        Save trained classifier to disk.
        
        We save:
        - The trained classifier
        - Training stats
        - Timestamp
        
        Note: We don't save the embedder (it's too large and can be reloaded)
        """
        if not self.is_trained:
            print("⚠️  Cannot save - classifier not trained!")
            return False
        
        filepath = filepath or os.path.join(MODEL_DIR, CLASSIFIER_FILE)
        
        try:
            save_data = {
                'classifier': self.classifier,
                'is_trained': self.is_trained,
                'training_accuracy': self.training_accuracy,
                'num_training_samples': self.num_training_samples,
                'saved_at': datetime.now().isoformat(),
                'embedding_model': EMBEDDING_MODEL,
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(save_data, f)
            
            print(f"💾 Classifier saved to: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving classifier: {e}")
            return False
    
    def load(self, filepath: str = None) -> bool:
        """
        Load trained classifier from disk.
        """
        filepath = filepath or os.path.join(MODEL_DIR, CLASSIFIER_FILE)
        
        if not os.path.exists(filepath):
            print(f"⚠️  No saved classifier found at: {filepath}")
            return False
        
        try:
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)
            
            self.classifier = save_data['classifier']
            self.is_trained = save_data['is_trained']
            self.training_accuracy = save_data.get('training_accuracy', 0.0)
            self.num_training_samples = save_data.get('num_training_samples', 0)
            
            print(f"📂 Classifier loaded from: {filepath}")
            print(f"   🎯 Accuracy: {self.training_accuracy:.1%}")
            print(f"   📊 Trained on: {self.num_training_samples} papers")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading classifier: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get classifier statistics."""
        return {
            'is_trained': self.is_trained,
            'training_accuracy': self.training_accuracy,
            'num_training_samples': self.num_training_samples,
            'embedding_model': EMBEDDING_MODEL,
        }


# =============================================================================
# LABELING HELPER
# =============================================================================

def label_papers_interactive(papers: List[Dict]) -> List[Dict]:
    """
    Interactive labeling session.
    
    Shows papers one by one and asks for your rating.
    
    Controls:
    - 'y' or '1' = Relevant (I want to read this!)
    - 'n' or '0' = Not relevant (Skip this)
    - 'q' = Quit labeling
    - 's' = Skip (don't label)
    """
    print("\n" + "=" * 60)
    print("🏷️  PAPER LABELING SESSION")
    print("=" * 60)
    print("\nFor each paper, enter:")
    print("  'y' or '1' = 👍 Relevant (I want to read this!)")
    print("  'n' or '0' = 👎 Not relevant")
    print("  's' = Skip this paper")
    print("  'q' = Quit labeling")
    print("-" * 60)
    
    labeled = []
    
    for i, paper in enumerate(papers):
        print(f"\n📄 Paper {i+1}/{len(papers)}")
        print(f"   Title: {paper['title'][:70]}...")
        print(f"   Category: {paper.get('primary_category', 'unknown')}")
        
        # Show truncated summary
        summary = paper.get('summary', '')[:200]
        if len(paper.get('summary', '')) > 200:
            summary += "..."
        print(f"   Summary: {summary}")
        
        print(f"   Link: {paper.get('abs_url', 'N/A')}")
        
        while True:
            response = input("\n   Your rating (y/n/s/q): ").strip().lower()
            
            if response in ['y', '1', 'yes']:
                paper['user_label'] = 1
                labeled.append(paper)
                print("   ✅ Marked as RELEVANT")
                break
            elif response in ['n', '0', 'no']:
                paper['user_label'] = 0
                labeled.append(paper)
                print("   ❌ Marked as NOT RELEVANT")
                break
            elif response == 's':
                print("   ⏭️  Skipped")
                break
            elif response == 'q':
                print("\n👋 Labeling session ended.")
                return labeled
            else:
                print("   Please enter 'y', 'n', 's', or 'q'")
    
    print(f"\n✅ Labeled {len(labeled)} papers!")
    return labeled


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    """Test the classifier with sample data."""
    
    if not ML_AVAILABLE:
        print("❌ Cannot run test - ML libraries not installed.")
        print("   Run: pip install scikit-learn sentence-transformers numpy")
        exit(1)
    
    print("=" * 60)
    print("🧪 CLASSIFIER TEST")
    print("=" * 60)
    
    # Create sample papers
    sample_papers = [
        # Relevant papers (deep learning, transformers, AI)
        {'title': 'Deep Learning for Natural Language Processing', 
         'summary': 'We present a novel neural network architecture for NLP tasks using transformers.',
         'user_label': 1},
        {'title': 'Attention Is All You Need: Transformer Architecture',
         'summary': 'This paper introduces the transformer model for sequence-to-sequence learning.',
         'user_label': 1},
        {'title': 'BERT: Pre-training of Deep Bidirectional Transformers',
         'summary': 'We introduce BERT, a new language representation model.',
         'user_label': 1},
        {'title': 'GPT-4 Technical Report',
         'summary': 'We present GPT-4, a large multimodal model capable of processing image and text inputs.',
         'user_label': 1},
        {'title': 'Neural Machine Translation by Jointly Learning to Align and Translate',
         'summary': 'We introduce attention mechanism for machine translation.',
         'user_label': 1},
        
        # Not relevant papers (other topics)
        {'title': 'Analysis of Climate Change Patterns in Arctic Regions',
         'summary': 'This study analyzes temperature changes in the Arctic over the past century.',
         'user_label': 0},
        {'title': 'Economic Impact of Trade Policies',
         'summary': 'We examine how tariffs affect international trade flows.',
         'user_label': 0},
        {'title': 'Quantum Mechanics of Black Holes',
         'summary': 'A theoretical study of Hawking radiation and information paradox.',
         'user_label': 0},
        {'title': 'Medieval History of European Kingdoms',
         'summary': 'An analysis of political structures in 12th century Europe.',
         'user_label': 0},
        {'title': 'Marine Biology: Coral Reef Ecosystems',
         'summary': 'Study of biodiversity in Pacific coral reef systems.',
         'user_label': 0},
    ]
    
    # Initialize classifier
    print("\n1️⃣ Initializing classifier...")
    classifier = PaperClassifier()
    
    # Train
    print("\n2️⃣ Training on sample data...")
    result = classifier.train(sample_papers)
    print(f"   Result: {result}")
    
    # Test predictions
    print("\n3️⃣ Testing predictions...")
    
    test_papers = [
        {'title': 'Large Language Models for Code Generation',
         'summary': 'We fine-tune GPT models for automated programming tasks.'},
        {'title': 'Effects of Deforestation on Amazon Wildlife',
         'summary': 'A study of species decline due to habitat loss.'},
        {'title': 'Diffusion Models for Image Generation',
         'summary': 'Novel approach to generating images using denoising diffusion.'},
    ]
    
    scores = classifier.predict(test_papers)
    
    print("\n   Predictions:")
    for paper, score in zip(test_papers, scores):
        emoji = "👍" if score > 0.5 else "👎"
        print(f"   {emoji} [{score:.1%}] {paper['title'][:50]}...")
    
    # Save
    print("\n4️⃣ Saving classifier...")
    classifier.save()
    
    # Load
    print("\n5️⃣ Loading classifier...")
    new_classifier = PaperClassifier()
    new_classifier.load()
    
    print("\n" + "=" * 60)
    print("✅ Classifier test complete!")
    print("=" * 60)