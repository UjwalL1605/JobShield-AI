"""
JobShield AI — Model Training Script

Trains a TF-IDF + Logistic Regression classifier for scam detection.
Outputs accuracy, precision, recall, F1, and saves the trained model.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def preprocess_text(text):
    """Basic text preprocessing."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    # Keep most characters — TF-IDF handles tokenization
    return text


def train_model(data_path=None, model_dir=None):
    """Train TF-IDF + Logistic Regression scam classifier."""

    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "data", "training_data.csv")

    if model_dir is None:
        model_dir = os.path.join(os.path.dirname(__file__), "models")

    os.makedirs(model_dir, exist_ok=True)

    # ── Load Data ────────────────────────────────────────────────────────────
    if not os.path.exists(data_path):
        print("⚠️  Training data not found. Generating synthetic dataset...")
        from dataset_generator import generate_dataset
        generate_dataset(output_path=data_path)

    df = pd.read_csv(data_path)
    print(f"📊 Loaded {len(df)} samples")
    print(f"   Scam: {(df['label'] == 1).sum()}, Legit: {(df['label'] == 0).sum()}")

    # ── Preprocess ───────────────────────────────────────────────────────────
    df["text_clean"] = df["text"].apply(preprocess_text)
    df = df[df["text_clean"].str.len() > 10]  # Remove very short texts

    X = df["text_clean"]
    y = df["label"]

    # ── Train/Test Split ─────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\n🔀 Split: {len(X_train)} train, {len(X_test)} test")

    # ── TF-IDF Vectorization ────────────────────────────────────────────────
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),       # Unigrams + bigrams
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
    )

    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)

    print(f"📐 TF-IDF features: {X_train_tfidf.shape[1]}")

    # ── Logistic Regression ──────────────────────────────────────────────────
    model = LogisticRegression(
        max_iter=1000,
        C=1.0,
        class_weight="balanced",
        solver="lbfgs",
        random_state=42,
    )

    model.fit(X_train_tfidf, y_train)

    # ── Evaluation ───────────────────────────────────────────────────────────
    y_pred = model.predict(X_test_tfidf)
    y_prob = model.predict_proba(X_test_tfidf)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("\n" + "=" * 50)
    print("📈 MODEL PERFORMANCE")
    print("=" * 50)
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")

    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Scam"]))

    print("🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"  FN={cm[1][0]}  TP={cm[1][1]}")

    # ── Cross Validation ─────────────────────────────────────────────────────
    X_all_tfidf = tfidf.transform(X)
    cv_scores = cross_val_score(model, X_all_tfidf, y, cv=5, scoring="f1")
    print(f"\n🔄 5-Fold CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ── Top Scam Indicators ──────────────────────────────────────────────────
    feature_names = tfidf.get_feature_names_out()
    coefs = model.coef_[0]
    top_scam_idx = np.argsort(coefs)[-20:][::-1]
    top_legit_idx = np.argsort(coefs)[:20]

    print("\n🚩 Top 20 Scam Indicators:")
    for idx in top_scam_idx:
        print(f"  {feature_names[idx]:30s} {coefs[idx]:.4f}")

    print("\n✅ Top 20 Legitimate Indicators:")
    for idx in top_legit_idx:
        print(f"  {feature_names[idx]:30s} {coefs[idx]:.4f}")

    # ── Save Model ───────────────────────────────────────────────────────────
    tfidf_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
    model_path = os.path.join(model_dir, "scam_classifier.pkl")

    joblib.dump(tfidf, tfidf_path)
    joblib.dump(model, model_path)

    print(f"\n💾 Model saved:")
    print(f"   Vectorizer: {tfidf_path}")
    print(f"   Classifier: {model_path}")
    print("\n✅ Training complete!")

    return tfidf, model


if __name__ == "__main__":
    train_model()
