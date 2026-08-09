"""
One-time merge script (v2 — fixed grouping): pulls the genuinely diverse
rows from synthetic_indian_jobs.csv into your existing training_data.csv
format.

v1 bug: it assigned ALL 400 new legit rows to a single template_id
("legit_ext_indianjobs"), which made GroupShuffleSplit/GroupKFold treat
them as one atomic block that either fully trains or fully tests. Since
that block is ~15% of the whole dataset, whichever fold it landed in
swung accuracy wildly — CV std deviation blew up from ±2.4% to ±22.8%.

Fix: we verified these 447 legit rows are ALL unique text (no shared
skeleton/find-replace pattern like your own dataset_generator.py
templates have), so grouping them together was never correct in the
first place. Each row now gets its own unique template_id, which is
the right choice for genuinely independent text — it lets the grouped
split behave like a normal per-example split for this portion of the
data, while still protecting against skeleton-leakage for anything
that IS templated (the 7 scam archetype groups from this same external
dataset DO share within-archetype structure and should stay grouped).

Run this from backend/ml/. Re-run dataset_generator.py first if you
want a clean base without last time's merge baked in.
"""

import pandas as pd
import os

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXISTING_PATH = os.path.join(BACKEND_ROOT, "ml", "data", "training_data.csv")
SOURCE_PATH = os.path.join(BACKEND_ROOT, "ml", "data", "synthetic_indian_jobs.csv")


def merge():
    if not os.path.exists(SOURCE_PATH):
        print(f"❌ Source file not found: {SOURCE_PATH}")
        print("   Copy synthetic_indian_jobs.csv into backend/ml/data/ first.")
        return

    existing = pd.read_csv(EXISTING_PATH)
    source = pd.read_csv(SOURCE_PATH)

    source = source.dropna(subset=["description"]).reset_index(drop=True)

    def make_template_id(row, idx):
        if row["label"] == 0:
            # Verified: 447/447 unique texts, no shared skeleton.
            # Each gets its own group so the grouped split treats them
            # as independent examples rather than one giant atomic block.
            return f"legit_ext_{idx}"
        # Scam archetypes DO share within-archetype structure (e.g. all
        # ~50 overseas_job_scam rows follow a similar "we require X for
        # our Dubai office" pattern) — keep these grouped by archetype
        # so the split still protects against that kind of leakage.
        return f"scam_ext_{row['archetype']}"

    new_rows = pd.DataFrame({
        "text": source["description"].astype(str).str.strip(),
        "label": source["label"].astype(int),
        "template_id": [make_template_id(row, idx) for idx, row in source.iterrows()],
    })

    before_count = len(existing)
    before_scam = (existing["label"] == 1).sum()
    before_legit = (existing["label"] == 0).sum()

    combined = pd.concat([existing, new_rows], ignore_index=True)

    before_dedup = len(combined)
    combined = combined.drop_duplicates(subset=["text"]).reset_index(drop=True)
    dupes_dropped = before_dedup - len(combined)

    combined.to_csv(EXISTING_PATH, index=False)

    after_scam = (combined["label"] == 1).sum()
    after_legit = (combined["label"] == 0).sum()

    print("✅ Merge complete (v2 — fixed grouping)")
    print(f"   Before: {before_count} rows ({before_scam} scam, {before_legit} legit)")
    print(f"   Added:  {len(new_rows)} rows from synthetic_indian_jobs.csv")
    if dupes_dropped:
        print(f"   Dropped {dupes_dropped} exact-duplicate rows")
    print(f"   After:  {len(combined)} rows ({after_scam} scam, {after_legit} legit)")
    print(f"   New unique templates added: {new_rows['template_id'].nunique()}")
    print(f"   Total unique templates now: {combined['template_id'].nunique()}")
    print(f"\n💾 Saved to: {EXISTING_PATH}")


if __name__ == "__main__":
    merge()