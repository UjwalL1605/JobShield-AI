"""
JobShield AI — NLP Analyzer Service

Wraps the trained TF-IDF + Logistic Regression model.
Provides scam probability predictions with feature importance explanations.
"""

import os
import re
import joblib
import numpy as np
from typing import Dict, Optional


class NLPAnalyzer:
    """Scam detection using trained ML model."""

    def __init__(self, model_dir: Optional[str] = None):
        if model_dir is None:
            model_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "ml", "models"
            )

        self.model_dir = model_dir
        self.vectorizer = None
        self.classifier = None
        self._loaded = False

    def load_model(self):
        """Load trained model from disk."""
        tfidf_path = os.path.join(self.model_dir, "tfidf_vectorizer.pkl")
        model_path = os.path.join(self.model_dir, "scam_classifier.pkl")

        if not os.path.exists(tfidf_path) or not os.path.exists(model_path):
            print("⚠️  Trained model not found. Run ml/train_model.py first.")
            return False

        self.vectorizer = joblib.load(tfidf_path)
        self.classifier = joblib.load(model_path)
        self._loaded = True
        print("✅ NLP model loaded successfully")
        return True

    def preprocess(self, text: str) -> str:
        """Preprocess text for model input."""
        if not isinstance(text, str):
            return ""
        text = text.lower().strip()
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        return text

    def predict(self, text: str) -> Dict:
        """
        Predict scam probability for given text.

        Returns:
            Dict with:
                - ml_score: float (0-100)
                - confidence: float (0-1)
                - top_features: list of contributing features
        """
        if not self._loaded:
            if not self.load_model():
                return {
                    "ml_score": 50.0,
                    "confidence": 0.0,
                    "top_features": [],
                    "model_available": False,
                }

        clean_text = self.preprocess(text)
        if not clean_text:
            return {
                "ml_score": 50.0,
                "confidence": 0.0,
                "top_features": [],
                "model_available": True,
            }

        # Vectorize
        X = self.vectorizer.transform([clean_text])

        # Predict probability
        proba = self.classifier.predict_proba(X)[0]
        scam_prob = proba[1]  # Probability of scam class
        confidence = max(proba)

        # Get top contributing features (XAI)
        top_features = self._get_top_features(X, n=10)

        return {
            "ml_score": round(scam_prob * 100, 2),
            "confidence": round(confidence, 4),
            "top_features": top_features,
            "model_available": True,
        }

    def _get_top_features(self, X, n: int = 10) -> list:
        """
        Get top N features contributing to the prediction.
        Uses model coefficients × TF-IDF values for interpretability.
        """
        if self.vectorizer is None or self.classifier is None:
            return []

        feature_names = self.vectorizer.get_feature_names_out()
        coefs = self.classifier.coef_[0]

        # Element-wise: TF-IDF value × coefficient
        tfidf_values = X.toarray()[0]
        contributions = tfidf_values * coefs

        # Get non-zero contributions
        nonzero_idx = np.nonzero(contributions)[0]
        if len(nonzero_idx) == 0:
            return []

        # Sort by absolute contribution
        sorted_idx = nonzero_idx[np.argsort(np.abs(contributions[nonzero_idx]))[::-1]]
        top_idx = sorted_idx[:n]

        features = []
        for idx in top_idx:
            features.append({
                "feature": feature_names[idx],
                "contribution": round(float(contributions[idx]), 4),
                "direction": "scam" if contributions[idx] > 0 else "legitimate",
            })

        return features


# ─── Singleton Instance ──────────────────────────────────────────────────────────
_analyzer_instance = None


def get_analyzer() -> NLPAnalyzer:
    """Get or create the singleton NLP analyzer."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = NLPAnalyzer()
        _analyzer_instance.load_model()
    return _analyzer_instance
