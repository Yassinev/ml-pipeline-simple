"""
Eval gate — run via `make eval-gate`.

1. Runs src.eval to regenerate reports/metrics.json from the golden set.
2. Loads configs/thresholds.yaml.
3. Asserts every gate defined in specs/EvalPlan.md passes.
4. Checks regression vs reports/metrics_prev.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from src.eval import run_eval

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT       = Path(__file__).parent.parent
GOLDEN     = ROOT / "data" / "golden_set.jsonl"
METRICS    = ROOT / "reports" / "metrics.json"
PREV       = ROOT / "reports" / "metrics_prev.json"
THRESHOLDS = ROOT / "configs" / "thresholds.yaml"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def metrics() -> dict:
    """Run evaluation and return fresh metrics."""
    return run_eval(str(GOLDEN), str(METRICS))


@pytest.fixture(scope="module")
def thresholds() -> dict:
    with open(THRESHOLDS) as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def prev_metrics() -> dict | None:
    if PREV.exists():
        with open(PREV) as fh:
            return json.load(fh)
    return None


# ════════════════════════════════════════════════════════════════════════════
#  GATE G1 — Overall Macro-F1
# ════════════════════════════════════════════════════════════════════════════

def test_G1_overall_macro_f1(metrics, thresholds):
    """G1: Overall Macro-F1 must meet the threshold in thresholds.yaml."""
    actual    = metrics["overall"]["macro_f1"]
    threshold = thresholds["overall"]["macro_f1"]
    assert actual >= threshold, (
        f"[G1] Overall Macro-F1 {actual:.4f} < threshold {threshold:.4f}"
    )


# ════════════════════════════════════════════════════════════════════════════
#  GATE G2 — Overall Accuracy
# ════════════════════════════════════════════════════════════════════════════

def test_G2_overall_accuracy(metrics, thresholds):
    """G2: Overall Accuracy must meet the threshold."""
    actual    = metrics["overall"]["accuracy"]
    threshold = thresholds["overall"]["accuracy"]
    assert actual >= threshold, (
        f"[G2] Accuracy {actual:.4f} < threshold {threshold:.4f}"
    )


# ════════════════════════════════════════════════════════════════════════════
#  GATE G3 — Coverage
# ════════════════════════════════════════════════════════════════════════════

def test_G3_coverage(metrics, thresholds):
    """G3: Coverage (1 - uncertain rate) must meet the threshold."""
    actual    = metrics["overall"]["coverage"]
    threshold = thresholds["overall"]["coverage"]
    assert actual >= threshold, (
        f"[G3] Coverage {actual:.4f} < threshold {threshold:.4f}"
    )


# ════════════════════════════════════════════════════════════════════════════
#  GATE G4 — Per-Slice F1
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("slice_name", [
    "positive", "negative", "neutral", "short_text", "long_text", "low_conf_gt"
])
def test_G4_slice_f1(slice_name, metrics, thresholds):
    """G4: Every slice must meet its individual F1 threshold."""
    slice_metrics = metrics.get("slices", {}).get(slice_name)
    if slice_metrics is None:
        pytest.skip(f"Slice '{slice_name}' not present in metrics.json")

    actual    = slice_metrics["f1"]
    threshold = thresholds["slices"].get(slice_name, {}).get("f1", 0.75)
    assert actual >= threshold, (
        f"[G4] Slice '{slice_name}' F1 {actual:.4f} < threshold {threshold:.4f}"
    )


# ════════════════════════════════════════════════════════════════════════════
#  GATE G5 — Regression vs previous run
# ════════════════════════════════════════════════════════════════════════════

def test_G5_macro_f1_regression(metrics, prev_metrics, thresholds):
    """G5: Macro-F1 must not drop by more than max_macro_f1_drop vs previous run."""
    if prev_metrics is None:
        pytest.skip("No previous metrics found — skipping regression check")

    current  = metrics["overall"]["macro_f1"]
    previous = prev_metrics["overall"]["macro_f1"]
    max_drop = thresholds["regression"]["max_macro_f1_drop"]
    delta    = current - previous

    assert delta >= -max_drop, (
        f"[G5] Macro-F1 regression: {previous:.4f} → {current:.4f} "
        f"(Δ={delta:+.4f}, allowed: ≥ -{max_drop})"
    )


@pytest.mark.parametrize("slice_name", [
    "positive", "negative", "neutral", "short_text", "long_text", "low_conf_gt"
])
def test_G5_slice_f1_regression(slice_name, metrics, prev_metrics, thresholds):
    """G5: No slice F1 may drop by more than max_slice_f1_drop vs previous run."""
    if prev_metrics is None:
        pytest.skip("No previous metrics found — skipping regression check")

    current_f1  = metrics.get("slices", {}).get(slice_name, {}).get("f1")
    previous_f1 = prev_metrics.get("slices", {}).get(slice_name, {}).get("f1")

    if current_f1 is None or previous_f1 is None:
        pytest.skip(f"Slice '{slice_name}' missing in current or previous metrics")

    max_drop = thresholds["regression"]["max_slice_f1_drop"]
    delta    = current_f1 - previous_f1

    assert delta >= -max_drop, (
        f"[G5] Slice '{slice_name}' F1 regression: "
        f"{previous_f1:.4f} → {current_f1:.4f} (Δ={delta:+.4f}, allowed: ≥ -{max_drop})"
    )


def test_G5_coverage_regression(metrics, prev_metrics, thresholds):
    """G5: Coverage must not drop by more than max_coverage_drop vs previous run."""
    if prev_metrics is None:
        pytest.skip("No previous metrics found — skipping regression check")

    current  = metrics["overall"]["coverage"]
    previous = prev_metrics["overall"]["coverage"]
    max_drop = thresholds["regression"]["max_coverage_drop"]
    delta    = current - previous

    assert delta >= -max_drop, (
        f"[G5] Coverage regression: {previous:.4f} → {current:.4f} "
        f"(Δ={delta:+.4f}, allowed: ≥ -{max_drop})"
    )
