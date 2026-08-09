"""
JobShield AI — Model Training Script (v3, Enhanced Feature Pipeline & Grouped Split)

Trains a FeatureUnion (TF-IDF + Domain Feature Extractor) + Logistic Regression classifier
for scam detection.
Splits by template_id (not by row) so the model cannot memorize template skeletons,
providing an honest and robust estimate.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)

from services.feature_extractor import ScamDomainFeatureExtractor


def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    return text.lower().strip()


def build_feature_pipeline():
    """Builds the composite feature extraction pipeline."""
    return FeatureUnion([
        ("tfidf", TfidfVectorizer(
            max_features=8000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.90,
            sublinear_tf=True,
        )),
        ("domain", ScamDomainFeatureExtractor()),
    ])


def train_model(data_path=None, model_dir=None):
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "data", "training_data.csv")

    if model_dir is None:
        model_dir = os.path.join(os.path.dirname(__file__), "models")

    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print("⚠️  Training data not found. Consolidating datasets...")
        from ml.consolidate_dataset import consolidate
        consolidate()

    df = pd.read_csv(data_path)

    if "template_id" not in df.columns:
        raise ValueError(
            "training_data.csv has no template_id column — run consolidate_dataset.py first."
        )

    print("=" * 65)
    print("🚀 JobShield AI — Model Training (v3 Enhanced Pipeline)")
    print("=" * 65)
    print(f"📊 Loaded {len(df)} samples")
    print(f"   ├── Scam (1):  {(df['label'] == 1).sum()} ({(df['label'] == 1).sum()/len(df)*100:.1f}%)")
    print(f"   └── Legit (0): {(df['label'] == 0).sum()} ({(df['label'] == 0).sum()/len(df)*100:.1f}%)")
    print(f"   Unique template groups: {df['template_id'].nunique()}")

    df["text_clean"] = df["text"].apply(preprocess_text)
    df = df[df["text_clean"].str.len() > 10].reset_index(drop=True)

    X = df["text_clean"]
    y = df["label"]
    groups = df["template_id"]

    # ── Group-aware Train/Test Split ─────────────────────────────────────────
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx].reset_index(drop=True), y.iloc[test_idx].reset_index(drop=True)
    groups_train = groups.iloc[train_idx]

    print(f"\n🔀 Grouped Split: {len(X_train)} train, {len(X_test)} test")
    print(f"   Train templates: {groups_train.nunique()}, Test templates: {groups.iloc[test_idx].nunique()}")

    # ── Feature Extraction ──────────────────────────────────────────────────
    feature_union = build_feature_pipeline()
    X_train_features = feature_union.fit_transform(X_train)
    X_test_features = feature_union.transform(X_test)

    print(f"📐 Total Features: {X_train_features.shape[1]}")

    # ── Classifier ──────────────────────────────────────────────────────────
    model = LogisticRegression(
        max_iter=1000,
        C=1.0,
        class_weight="balanced",
        solver="lbfgs",
        random_state=42,
    )
    model.fit(X_train_features, y_train)

    # ── Evaluation on Grouped Test Set ───────────────────────────────────────
    y_pred = model.predict(X_test_features)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("\n" + "=" * 55)
    print("📈 MODEL PERFORMANCE (Grouped Test Split — Honest Estimate)")
    print("=" * 55)
    print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")

    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Scam"]))

    print("🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"  FN={cm[1][0]}  TP={cm[1][1]}")

    # ── Group-aware Cross Validation ─────────────────────────────────────────
    cv_pipeline = Pipeline([
        ("features", build_feature_pipeline()),
        ("clf", LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced", solver="lbfgs", random_state=42)),
    ])
    n_groups = groups.nunique()
    cv_folds = min(5, n_groups)
    gkf = GroupKFold(n_splits=cv_folds)
    cv_scores = cross_val_score(cv_pipeline, X, y, groups=groups, cv=gkf, scoring="f1")
    print(f"\n🔄 {cv_folds}-Fold Group CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ── Top Indicators ───────────────────────────────────────────────────────
    feature_names = feature_union.get_feature_names_out()
    coefs = model.coef_[0]
    top_scam_idx = np.argsort(coefs)[-20:][::-1]
    top_legit_idx = np.argsort(coefs)[:20]

    print("\n🚩 Top 20 Scam Indicators:")
    for idx in top_scam_idx:
        fname = str(feature_names[idx]).replace("tfidf__", "").replace("domain__", "")
        print(f"  {fname:35s} {coefs[idx]:.4f}")

    print("\n✅ Top 20 Legitimate Indicators:")
    for idx in top_legit_idx:
        fname = str(feature_names[idx]).replace("tfidf__", "").replace("domain__", "")
        print(f"  {fname:35s} {coefs[idx]:.4f}")

    # ── Save Final Production Model (Retrained on ALL Clean Data) ───────────
    print("\n💾 Retraining on 100% of consolidated clean data for production...")
    final_feature_pipe = build_feature_pipeline()
    X_all_features = final_feature_pipe.fit_transform(X)

    final_model = LogisticRegression(
        max_iter=1000, C=1.0, class_weight="balanced", solver="lbfgs", random_state=42
    )
    final_model.fit(X_all_features, y)

    tfidf_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
    model_path = os.path.join(model_dir, "scam_classifier.pkl")
    joblib.dump(final_feature_pipe, tfidf_path)
    joblib.dump(final_model, model_path)

    print(f"✅ Saved production artifacts:")
    print(f"   ├── Feature Pipeline: {tfidf_path}")
    print(f"   └── Classifier Model: {model_path}")
    print("=" * 65)

    return final_feature_pipe, final_model


if __name__ == "__main__":
    train_model()