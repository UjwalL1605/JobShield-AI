"""
JobShield AI — Combined Pipeline Evaluation

Tests the FULL production pipeline (ML + rule engine + email/salary/known-scam
checks, exactly as combined in routers/analyze.py) against the same 27
hand-written real-world holdout examples used in evaluate_real.py.

This tells you whether the negation fix in rule_engine.py actually improved
the end-to-end system the user experiences, not just the rule engine alone.
"""

import asyncio
import os
import sys
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)

# backend/ is the parent of ml/ — needed to import routers.analyze
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from evaluate_real import TEST_SET, evaluate as evaluate_real   # reuse the same 27 examples + live accuracy
from routers.analyze import _run_analysis_async                  # the real production pipeline

SCAM_THRESHOLD = 50.0  # combined score >= this => classified as scam


async def _evaluate_pipeline_async():
    # Get the raw-ML-only baseline live, computed fresh against whatever
    # model is currently saved in ml/models/ — no more hardcoded numbers
    # going stale after every retrain. Runs silently (verbose=False) since
    # we only want the number here, not a duplicate full report.
    ml_only_accuracy = evaluate_real(verbose=False)

    y_true = []
    y_pred = []
    results = []

    for text, true_label in TEST_SET:
        result = await _run_analysis_async(text, "job_posting")
        combined_score = result["scam_probability"]
        predicted_label = 1 if combined_score >= SCAM_THRESHOLD else 0

        y_true.append(true_label)
        y_pred.append(predicted_label)
        results.append({
            "text": text,
            "true": true_label,
            "pred": predicted_label,
            "combined_score": combined_score,
            "ml_score": result["ml_score"],
            "rule_score": result["rule_score"],
            "trust_level": result["trust_level"],
        })

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    print("=" * 60)
    print("📈 FULL PIPELINE EVALUATION (ML + Rules + Email/Salary/DB)")
    print("=" * 60)
    print(f"  Samples:   {len(TEST_SET)}")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")

    print("\n📋 Classification Report:")
    print(classification_report(y_true, y_pred, target_names=["Legitimate", "Scam"]))

    print("🔢 Confusion Matrix:")
    cm = confusion_matrix(y_true, y_pred)
    print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"  FN={cm[1][0]}  TP={cm[1][1]}")

    print("\n❌ Misclassified examples (combined pipeline):")
    label_name = {0: "Legit", 1: "Scam"}
    for r in results:
        if r["pred"] != r["true"]:
            print(f"  True={label_name[r['true']]:6s} Pred={label_name[r['pred']]:6s} "
                  f"| combined={r['combined_score']:.1f} (ml={r['ml_score']:.1f}, rule={r['rule_score']:.1f}) "
                  f"trust={r['trust_level']}")
            print(f"    {r['text'][:100]}")

    print(f"\n📊 Compare to raw-ML-only baseline: {ml_only_accuracy*100:.2f}% accuracy (from evaluate_real.py, computed live)")
    print(f"   Full pipeline accuracy: {accuracy*100:.2f}%")
    print("\n✅ Evaluation complete!")
    return accuracy


def evaluate():
    return asyncio.run(_evaluate_pipeline_async())


if __name__ == "__main__":
    evaluate()