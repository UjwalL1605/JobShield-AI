"""
JobShield AI — Dataset Consolidation and Deduplication Script

Merges:
1. Deduplicated synthetic samples from dataset_generator.py
2. Real-world legitimate LinkedIn JDs & corporate recruitment emails from Indian Job Scam Dataset.csv
3. Real-world Indian recruitment scams and WhatsApp job offer scams from Indian Job Scam Dataset.csv
4. Archetype-diverse samples from synthetic_indian_jobs.csv

Enforces 100% text uniqueness (zero exact or whitespace-normalized duplicates)
and maintains proper template_id groups for honest GroupKFold cross-validation.
"""

import os
import sys
import re
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from ml.dataset_generator import generate_dataset


def normalize_text(text: str) -> str:
    """Normalize text for strict deduplication matching."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    return re.sub(r"\s+", " ", text)


def consolidate():
    ml_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(ml_dir, "data")
    output_path = os.path.join(data_dir, "training_data.csv")
    indian_dataset_path = os.path.join(data_dir, "Indian Job Scam Dataset.csv")
    synth_dataset_path = os.path.join(data_dir, "synthetic_indian_jobs.csv")

    print("=" * 65)
    print("🚀 JobShield AI — Consolidating & Deduplicating Training Dataset")
    print("=" * 65)

    # 1. Generate clean synthetic base dataset (1,400 scam, 1,400 legit unique)
    print("1️⃣ Generating clean synthetic dataset...")
    df_synthetic = generate_dataset(num_scam=1400, num_legit=1400, output_path=output_path)

    # 2. Extract from Indian Job Scam Dataset.csv
    indian_rows = []
    if os.path.exists(indian_dataset_path):
        print(f"\n2️⃣ Extracting real-world samples from: {os.path.basename(indian_dataset_path)}")
        df_ind = pd.read_csv(indian_dataset_path)

        # 2a. Legit Emails (fraudulent == 0.0, source == 'email')
        for idx, row in df_ind[df_ind["source"] == "email"].iterrows():
            msg = str(row["message"]).strip()
            if len(msg) > 15:
                indian_rows.append({
                    "text": msg,
                    "label": 0,
                    "template_id": f"legit_email_{idx}",
                })

        # 2b. Legit LinkedIn (fraudulent == 0.0, source == 'linkedin')
        for idx, row in df_ind[df_ind["source"] == "linkedin"].iterrows():
            msg = str(row["message"]).strip()
            if len(msg) > 15:
                indian_rows.append({
                    "text": msg,
                    "label": 0,
                    "template_id": f"legit_linkedin_{idx}",
                })

        # 2c. Recruitment Scams (fraudulent == 1.0, source == 'recruitment')
        for idx, row in df_ind[df_ind["source"] == "recruitment"].iterrows():
            msg = str(row["message"]).strip()
            stype = str(row.get("scam_type", "recruitment_scam")).replace(" ", "_").lower()
            if len(msg) > 15:
                indian_rows.append({
                    "text": msg,
                    "label": 1,
                    "template_id": f"scam_recruit_{stype}_{idx % 30}",
                })

        # 2d. WhatsApp Job Offer Scams & Key Cyber Job Scams (deduplicated)
        wa_rows = df_ind[df_ind["source"] == "whatsapp"]
        for stype, group in wa_rows.groupby("scam_type"):
            unique_msgs = group["message"].dropna().drop_duplicates().tolist()
            # Focus on Fake Job Offer Scams and relevant employment/investment scams
            sample_limit = 250 if stype == "Fake Job Offer Scam" else 40
            stype_key = str(stype).replace(" ", "_").lower()
            for i, msg in enumerate(unique_msgs[:sample_limit]):
                msg = str(msg).strip()
                if len(msg) > 15:
                    indian_rows.append({
                        "text": msg,
                        "label": 1,
                        "template_id": f"scam_wa_{stype_key}_{i % 20}",
                    })

        print(f"   Extracted {len(indian_rows)} rows from Indian Job Scam Dataset")
    else:
        print(f"⚠️  Indian Job Scam Dataset not found at: {indian_dataset_path}")

    # 3. Extract from synthetic_indian_jobs.csv
    synth_rows = []
    if os.path.exists(synth_dataset_path):
        print(f"\n3️⃣ Extracting samples from: {os.path.basename(synth_dataset_path)}")
        df_syn = pd.read_csv(synth_dataset_path)
        for idx, row in df_syn.iterrows():
            desc = str(row.get("description", "")).strip()
            if len(desc) > 15:
                lbl = int(row["label"])
                arch = str(row.get("archetype", "legit" if lbl == 0 else "scam"))
                t_id = f"synth_legit_{idx}" if lbl == 0 else f"synth_scam_{arch}"
                synth_rows.append({
                    "text": desc,
                    "label": lbl,
                    "template_id": t_id,
                })
        print(f"   Extracted {len(synth_rows)} rows from synthetic_indian_jobs.csv")
    else:
        print(f"⚠️  synthetic_indian_jobs.csv not found at: {synth_dataset_path}")

    # 4. Combine and perform strict deduplication
    print("\n4️⃣ Merging and deduplicating all sources...")
    all_dfs = [df_synthetic]
    if indian_rows:
        all_dfs.append(pd.DataFrame(indian_rows))
    if synth_rows:
        all_dfs.append(pd.DataFrame(synth_rows))

    df_combined = pd.concat(all_dfs, ignore_index=True)
    before_count = len(df_combined)

    # Normalize for deduplication
    df_combined["norm_key"] = df_combined["text"].apply(normalize_text)
    df_combined = df_combined[df_combined["norm_key"].str.len() > 10]
    df_dedup = df_combined.drop_duplicates(subset=["norm_key"]).reset_index(drop=True)
    df_dedup = df_dedup.drop(columns=["norm_key"])

    dupes_removed = before_count - len(df_dedup)

    # Save final consolidated dataset
    df_dedup.to_csv(output_path, index=False)

    scam_count = (df_dedup["label"] == 1).sum()
    legit_count = (df_dedup["label"] == 0).sum()
    unique_templates = df_dedup["template_id"].nunique()

    print("=" * 65)
    print("✅ DATASET CONSOLIDATION COMPLETE")
    print("=" * 65)
    print(f"  Total samples before dedup: {before_count}")
    print(f"  Duplicates removed:         {dupes_removed}")
    print(f"  Final clean dataset size:   {len(df_dedup)} rows")
    print(f"  ├── Scam samples (1):       {scam_count} ({scam_count/len(df_dedup)*100:.1f}%)")
    print(f"  └── Legit samples (0):      {legit_count} ({legit_count/len(df_dedup)*100:.1f}%)")
    print(f"  Unique template groups:     {unique_templates}")
    print(f"💾 Saved cleanly to: {output_path}")

    return df_dedup


if __name__ == "__main__":
    consolidate()
