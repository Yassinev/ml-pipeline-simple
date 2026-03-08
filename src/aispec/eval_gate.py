"""
Eval Gate
Compares metrics in reports/metrics_example.json against thresholds in configs/thresholds.yaml.
Exits with code 1 if any hard-gate metric is below its threshold.
Writes reports/eval_report.json with detailed pass/fail status.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

HARD_GATE_METRICS = {"accuracy", "f1_score"}
SOFT_WARN_METRICS = {"precision", "recall"}

# latency is inverted (lower is better)
INVERTED_METRICS = {"latency_p95_ms"}


def main() -> int:
    metrics_path = Path("reports/metrics_example.json")
    thresholds_path = Path("configs/thresholds.yaml")

    for path in [metrics_path, thresholds_path]:
        if not path.exists():
            print(f"ERROR: Required file not found: {path}", file=sys.stderr)
            return 1

    with metrics_path.open() as f:
        metrics: dict = json.load(f)

    with thresholds_path.open() as f:
        config: dict = yaml.safe_load(f)

    thresholds: dict = config.get("thresholds", {})

    results = {}
    failed_hard = []
    soft_warnings = []

    print("=" * 60)
    print("EVAL GATE REPORT")
    print("=" * 60)

    for metric, threshold in thresholds.items():
        actual = metrics.get(metric)
        if actual is None:
            print(f"  ⚠️  {metric}: not found in metrics file (skipped)")
            results[metric] = {"status": "missing", "threshold": threshold, "actual": None}
            continue

        if metric in INVERTED_METRICS:
            passed = float(actual) <= float(threshold)
            cmp_str = f"{actual} ≤ {threshold}"
        else:
            passed = float(actual) >= float(threshold)
            cmp_str = f"{actual} ≥ {threshold}"

        status = "pass" if passed else "fail"
        icon = "✅" if passed else "❌"
        gate_type = "HARD" if metric in HARD_GATE_METRICS else "SOFT"

        print(f"  {icon} [{gate_type}] {metric}: {cmp_str} → {status.upper()}")

        results[metric] = {
            "status": status,
            "gate_type": gate_type,
            "threshold": threshold,
            "actual": actual,
            "passes": passed,
        }

        if not passed:
            if metric in HARD_GATE_METRICS:
                failed_hard.append(metric)
            else:
                soft_warnings.append(metric)

    print("=" * 60)

    overall_pass = len(failed_hard) == 0
    print(f"\n{'✅ EVAL GATE PASSED' if overall_pass else '❌ EVAL GATE FAILED'}")
    if failed_hard:
        print(f"  Failed hard gates: {failed_hard}")
    if soft_warnings:
        print(f"  Soft warnings: {soft_warnings}")

    # Write report
    report = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "overall_pass": overall_pass,
        "failed_hard_gates": failed_hard,
        "soft_warnings": soft_warnings,
        "metrics": results,
    }
    report_path = Path("reports/eval_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport written to: {report_path}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
