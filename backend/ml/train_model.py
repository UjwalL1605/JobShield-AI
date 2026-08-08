"""
JobShield AI — Model Training Script (v2, grouped split)

Trains a TF-IDF + Logistic Regression classifier for scam detection.
Splits by template_id (not by row) so the model can't just memorize
template shape — this gives an honest accuracy estimate.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    return text.lower().strip()


def train_model(data_path=None, model_dir=None):
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "data", "training_data.csv")

    if model_dir is None:
        model_dir = os.path.join(os.path.dirname(__file__), "models")

    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print("⚠️  Training data not found. Generating synthetic dataset...")
        from dataset_generator import generate_dataset
        generate_dataset(output_path=data_path)

    df = pd.read_csv(data_path)

    if "template_id" not in df.columns:
        raise ValueError(
            "training_data.csv has no template_id column — delete it and rerun "
            "dataset_generator.py with the updated script to regenerate it."
        )

    print(f"📊 Loaded {len(df)} samples")
    print(f"   Scam: {(df['label'] == 1).sum()}, Legit: {(df['label'] == 0).sum()}")
    print(f"   Unique templates: {df['template_id'].nunique()}")

    df["text_clean"] = df["text"].apply(preprocess_text)
    df = df[df["text_clean"].str.len() > 10].reset_index(drop=True)

    X = df["text_clean"]
    y = df["label"]
    groups = df["template_id"]

    # ── Group-aware Train/Test Split ─────────────────────────────────────────
    # Same template can NEVER appear in both train and test — this is what
    # makes the resulting score trustworthy instead of inflated.
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx].reset_index(drop=True), y.iloc[test_idx].reset_index(drop=True)
    groups_train = groups.iloc[train_idx]

    print(f"\n🔀 Split: {len(X_train)} train, {len(X_test)} test")
    print(f"   Train templates: {groups_train.nunique()}, Test templates: {groups.iloc[test_idx].nunique()}")

    # ── TF-IDF Vectorization ────────────────────────────────────────────────
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
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

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("\n" + "=" * 50)
    print("📈 MODEL PERFORMANCE (grouped split — honest estimate)")
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

    # ── Misclassified Examples ───────────────────────────────────────────────
    X_test_reset = X_test.reset_index(drop=True)
    wrong_mask = y_pred != y_test.values
    print(f"\n❌ Misclassified: {wrong_mask.sum()} out of {len(y_test)}")
    label_name = {0: "Legit", 1: "Scam"}
    for text, true_label, pred_label in list(zip(
        X_test_reset[wrong_mask], y_test[wrong_mask], y_pred[wrong_mask]
    ))[:10]:
        print(f"  True={label_name[true_label]:6s} Pred={label_name[pred_label]:6s} | {text[:100]}")

    # ── Group-aware Cross Validation ─────────────────────────────────────────
    cv_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2),
                                   min_df=2, max_df=0.95, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, C=1.0,
                                    class_weight="balanced", solver="lbfgs", random_state=42)),
    ])
    n_groups = groups.nunique()
    cv_folds = min(5, n_groups)
    gkf = GroupKFold(n_splits=cv_folds)
    cv_scores = cross_val_score(cv_pipeline, X, y, groups=groups, cv=gkf, scoring="f1")
    print(f"\n🔄 {cv_folds}-Fold Group CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ── Top Indicators ───────────────────────────────────────────────────────
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

    # ── Save Model (retrained on ALL data for the actual deployed app) ───────
    final_tfidf = TfidfVectorizer(
        max_features=5000, ngram_range=(1, 2), min_df=2, max_df=0.95, sublinear_tf=True
    )
    X_all_tfidf = final_tfidf.fit_transform(X)
    final_model = LogisticRegression(
        max_iter=1000, C=1.0, class_weight="balanced", solver="lbfgs", random_state=42
    )
    final_model.fit(X_all_tfidf, y)

    tfidf_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
    model_path = os.path.join(model_dir, "scam_classifier.pkl")
    joblib.dump(final_tfidf, tfidf_path)
    joblib.dump(final_model, model_path)

    print(f"\n💾 Final model (trained on all data) saved:")
    print(f"   Vectorizer: {tfidf_path}")
    print(f"   Classifier: {model_path}")
    print("\n✅ Training complete!")

    return final_tfidf, final_model


if __name__ == "__main__":
    train_model()