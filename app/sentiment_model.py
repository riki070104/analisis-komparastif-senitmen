import re
import os
import pickle
from .ml_pipeline.preprocessing_utils import preprocess_text
from .ml_pipeline.custom_ml import CustomTfidfVectorizer, CustomDecisionTree, CustomRandomForest

# Paths to model files
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'vectorizer.pkl')
RF_MODEL_PATH = os.path.join(MODEL_DIR, 'rf_model.pkl')

# Global variables to store loaded models
_vectorizer = None
_rf_model = None

def _load_models():
    global _vectorizer, _rf_model
    if _vectorizer is None or _rf_model is None:
        try:
            if os.path.exists(VECTORIZER_PATH) and os.path.exists(RF_MODEL_PATH):
                with open(VECTORIZER_PATH, 'rb') as f:
                    _vectorizer = pickle.load(f)
                with open(RF_MODEL_PATH, 'rb') as f:
                    _rf_model = pickle.load(f)
            else:
                print("Warning: Model files not found. Please run train_model.py first.")
                return False
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
    return True

def normalize_text(text):
    """Normalize text untuk analisis sentiment"""
    return preprocess_text(text)

def analyze_sentiment(text):
    """
    Analisis sentiment text menggunakan Random Forest Classifier
    Return: (sentiment, confidence)
    sentiment: 'positive', 'negative', atau 'neutral'
    confidence: float antara 0-1
    """
    if not text or len(text.strip()) == 0:
        return 'neutral', 0.0
    
    # Load model if not already loaded
    if not _load_models():
        # Fallback if model is not trained yet
        return 'neutral', 0.5
    
    normalized_text = normalize_text(text)
    
    try:
        # Transform text
        X = _vectorizer.transform([normalized_text])
        
        # Predict sentiment and probabilities
        sentiment = _rf_model.predict(X)[0]
        probabilities = _rf_model.predict_proba(X)[0]
        
        # Get the confidence score (max probability)
        confidence = float(max(probabilities))
        
        return sentiment, confidence
    except Exception as e:
        print(f"Prediction error: {e}")
        return 'neutral', 0.0
