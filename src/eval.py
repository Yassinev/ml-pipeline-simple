"""
Evaluation runner.

Usage:
    python -m src.eval [--golden data/golden_set.jsonl] [--out reports/metrics.json]

Reads a golden-set JSONL file, runs predictions through src.model.predict,
computes metrics per spec/EvalPlan.md, and writes reports/metrics.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

from src.model import predict


def f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def compute_metrics(records: list[dict]) -> dict:
    """Compute overall + slice metrics from a list of {label, prediction} dicts."""
    labels = ["positive", "negative", "neutral"]

    # Per-class counts
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)
    total = len(records)
    correct = 0
    uncertain_count = 0

    for r in records:
        gt = r["label"]
        pred = r["prediction"]
        if pred == "uncertain":
            uncertain_count += 1
            continue
        if pred == gt:
            correct += 1
            tp[gt] += 1
        else:
            fp[pred] += 1
            fn[gt] += 1

    # Per-class F1
    per_class_f1 = {}
    for lbl in labels:
        prec = tp[lbl] / (tp[lbl] + fp[lbl]) if (tp[lbl] + fp[lbl]) > 0 else 0.0
        rec = tp[lbl] / (tp[lbl] + fn[lbl]) if (tp[lbl] + fn[lbl]) > 0 else 0.0
        per_class_f1[lbl] = round(f1(prec, rec), 4)

    non_uncertain = total - uncertain_count
    accuracy = round(correct / non_uncertain, 4) if non_uncertain > 0 else 0.0
    macro_f1 = round(sum(per_class_f1.values()) / len(labels), 4)
    coverage = round(non_uncertain / total, 4) if total > 0 else 0.0

    # Slices — macro F1 over classes *present* in the subset
    def slice_f1(subset: list[dict]) -> float | None:
        """Return macro-F1 over classes present in the subset, or None if empty."""
        if not subset:
            return None
        present_classes = {r["label"] for r in subset if r["label"] in labels}
        if not present_classes:
            return None
        s_tp = defaultdict(int)
        s_fp = defaultdict(int)
        s_fn = defaultdict(int)
        for r in subset:
            gt = r["label"]
            pred = r["prediction"]
            if pred == "uncertain":
                continue
            if pred == gt:
                s_tp[gt] += 1
            else:
                s_fp[pred] += 1
                s_fn[gt] += 1
        class_f1s = []
        for lbl in present_classes:
            prec = s_tp[lbl] / (s_tp[lbl] + s_fp[lbl]) if (s_tp[lbl] + s_fp[lbl]) > 0 else 0.0
            rec = s_tp[lbl] / (s_tp[lbl] + s_fn[lbl]) if (s_tp[lbl] + s_fn[lbl]) > 0 else 0.0
            class_f1s.append(f1(prec, rec))
        return round(sum(class_f1s) / len(present_classes), 4)

    def make_slice(subset):
        v = slice_f1(subset)
        return {"f1": v} if v is not None else None

    raw_slices = {
        "positive":    make_slice([r for r in records if r["label"] == "positive"]),
        "negative":    make_slice([r for r in records if r["label"] == "negative"]),
        "neutral":     make_slice([r for r in records if r["label"] == "neutral"]),
        "short_text":  make_slice([r for r in records if len(r["text"]) <= 50]),
        "long_text":   make_slice([r for r in records if len(r["text"]) > 200]),
        "low_conf_gt": make_slice([r for r in records if r.get("confidence_gt", 1.0) < 0.80]),
    }
    slices = {k: v for k, v in raw_slices.items() if v is not None}

    return {
        "overall": {
            "macro_f1": macro_f1,
            "accuracy": accuracy,
            "coverage": coverage,
        },
        "slices": slices,
    }


def run_eval(golden_path: str, out_path: str) -> dict:
    records = []
    with open(golden_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            result = predict(obj["text"])
            obj["prediction"] = result["label"]
            records.append(obj)

    metrics = compute_metrics(records)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(metrics, fh, indent=2)

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden", default="data/golden_set.jsonl")
    parser.add_argument("--out", default="reports/metrics.json")
    args = parser.parse_args()

    metrics = run_eval(args.golden, args.out)
    print(json.dumps(metrics, indent=2))
