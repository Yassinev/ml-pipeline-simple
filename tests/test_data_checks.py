"""
Automated data checks — run via `make data-check`.

Implements ≥ 10 checks as required by HW3:
  Syntactic (3):  S1 required columns present, S2 no empty text, S3 valid label values
  Structural (4): S4 no duplicate (text, label) pairs, S5 no train/val leakage,
                  S6 all label classes present in train, S7 confidence_gt in [0,1]
  Statistical (3): S8 class imbalance < 70 %, S9 distribution shift proxy (text length KS),
                   S10 source dominance < 80 %
"""
import json
from pathlib import Path

import pandas as pd
import numpy as np
import pytest
from scipy import stats

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
TRAIN_CSV = ROOT / "data" / "sample_train.csv"
VAL_CSV   = ROOT / "data" / "sample_val.csv"
GOLDEN    = ROOT / "data" / "golden_set.jsonl"

REQUIRED_COLS = {"id", "text", "label", "source", "confidence_gt"}
VALID_LABELS  = {"positive", "negative", "neutral"}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def train_df():
    return pd.read_csv(TRAIN_CSV)


@pytest.fixture(scope="module")
def val_df():
    return pd.read_csv(VAL_CSV)


@pytest.fixture(scope="module")
def golden_records():
    records = []
    with open(GOLDEN) as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ════════════════════════════════════════════════════════════════════════════
#  SYNTACTIC CHECKS
# ════════════════════════════════════════════════════════════════════════════

class TestSyntactic:

    def test_S1_required_columns_present(self, train_df):
        """S1 — All required columns must be present in the CSV."""
        missing = REQUIRED_COLS - set(train_df.columns)
        assert not missing, f"Missing columns in train CSV: {missing}"

    def test_S2_no_empty_text(self, train_df, val_df):
        """S2 — No row may have empty or whitespace-only text."""
        for name, df in [("train", train_df), ("val", val_df)]:
            empty_mask = df["text"].isna() | (df["text"].str.strip() == "")
            n_empty = empty_mask.sum()
            assert n_empty == 0, f"{n_empty} empty 'text' rows found in {name} split"

    def test_S3_valid_label_values(self, train_df, val_df):
        """S3 — Every label must be one of the allowed class values."""
        for name, df in [("train", train_df), ("val", val_df)]:
            invalid = set(df["label"].unique()) - VALID_LABELS
            assert not invalid, f"Invalid labels in {name}: {invalid}"


# ════════════════════════════════════════════════════════════════════════════
#  STRUCTURAL CHECKS
# ════════════════════════════════════════════════════════════════════════════

class TestStructural:

    def test_S4_no_duplicate_text_label_pairs(self, train_df):
        """S4 — (text, label) pairs must be unique within the training split."""
        dupes = train_df.duplicated(subset=["text", "label"])
        n = dupes.sum()
        assert n == 0, f"{n} duplicate (text, label) pairs found in train split"

    def test_S5_no_train_val_leakage(self, train_df, val_df):
        """S5 — No text appearing in both train and val splits (leakage)."""
        train_texts = set(train_df["text"].str.strip().str.lower())
        val_texts   = set(val_df["text"].str.strip().str.lower())
        leakage = train_texts & val_texts
        assert not leakage, (
            f"{len(leakage)} overlapping texts between train and val: "
            f"{list(leakage)[:3]}..."
        )

    def test_S6_all_classes_present_in_train(self, train_df):
        """S6 — Every class must have at least one example in training data."""
        present = set(train_df["label"].unique())
        missing = VALID_LABELS - present
        assert not missing, f"Classes missing from train split: {missing}"

    def test_S7_confidence_gt_range(self, train_df):
        """S7 — confidence_gt must be in [0.0, 1.0] where present."""
        non_null = train_df["confidence_gt"].dropna()
        out_of_range = non_null[(non_null < 0.0) | (non_null > 1.0)]
        assert len(out_of_range) == 0, (
            f"{len(out_of_range)} confidence_gt values outside [0,1]"
        )


# ════════════════════════════════════════════════════════════════════════════
#  STATISTICAL CHECKS
# ════════════════════════════════════════════════════════════════════════════

class TestStatistical:

    def test_S8_class_imbalance(self, train_df):
        """S8 — No single class may exceed 70 % of the training set."""
        counts = train_df["label"].value_counts(normalize=True)
        dominant_class = counts.idxmax()
        dominant_pct = counts.max()
        assert dominant_pct < 0.70, (
            f"Class '{dominant_class}' dominates at {dominant_pct:.1%} (threshold: 70 %)"
        )

    def test_S9_train_val_text_length_distribution_shift(self, train_df, val_df):
        """
        S9 — Distribution-shift proxy: Kolmogorov-Smirnov test on text-length
        distributions between train and val.  p-value > 0.05 means no significant
        shift detected.
        """
        train_lengths = train_df["text"].str.len().values
        val_lengths   = val_df["text"].str.len().values
        stat, p_value = stats.ks_2samp(train_lengths, val_lengths)
        assert p_value > 0.05, (
            f"Significant text-length distribution shift detected between train "
            f"and val (KS statistic={stat:.4f}, p={p_value:.4f}). "
            "Check for sampling bias."
        )

    def test_S10_source_dominance(self, train_df):
        """S10 — No single 'source' value may account for > 80 % of training rows."""
        non_null = train_df["source"].dropna()
        if len(non_null) == 0:
            pytest.skip("No 'source' values present — skipping dominance check")
        counts = non_null.value_counts(normalize=True)
        dominant_source = counts.idxmax()
        dominant_pct = counts.max()
        assert dominant_pct < 0.80, (
            f"Source '{dominant_source}' dominates at {dominant_pct:.1%} (threshold: 80 %)"
        )


# ════════════════════════════════════════════════════════════════════════════
#  GOLDEN SET CHECKS
# ════════════════════════════════════════════════════════════════════════════

class TestGoldenSet:

    def test_golden_set_has_minimum_examples(self, golden_records):
        """Golden set must have at least 20 examples as per HW4 requirement."""
        assert len(golden_records) >= 20, (
            f"Golden set has only {len(golden_records)} examples; need ≥ 20"
        )

    def test_golden_set_all_classes_balanced(self, golden_records):
        """Each class in the golden set must have at least 5 examples."""
        from collections import Counter
        counts = Counter(r["label"] for r in golden_records)
        for lbl in VALID_LABELS - {"uncertain"}:  # uncertain not expected in golden set
            assert counts.get(lbl, 0) >= 5, (
                f"Class '{lbl}' has only {counts.get(lbl, 0)} examples in golden set"
            )

    def test_golden_set_schema(self, golden_records):
        """Every golden-set record must have id, text, and label fields."""
        for i, r in enumerate(golden_records):
            for field in ("id", "text", "label"):
                assert field in r, f"Golden set record {i} missing field '{field}'"
            assert r["label"] in VALID_LABELS, (
                f"Golden set record {i} has invalid label '{r['label']}'"
            )
