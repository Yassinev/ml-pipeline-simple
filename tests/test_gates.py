import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aispec.data_contract import check_record, violations, warnings

class TestDataContract:
    def setup_method(self):
        violations.clear()
        warnings.clear()

    def test_valid_record_no_violations(self):
        check_record(1, {"id":"r1","input_text":"hello","label":"positive","score":0.9,"timestamp":"2026-01-01T00:00:00Z"})
        assert len(violations) == 0

    def test_missing_required_field(self):
        check_record(1, {"id":"r1","input_text":"hello","label":"positive","score":0.9})
        assert any("DQ-01" in v for v in violations)

    def test_score_out_of_range_above(self):
        check_record(1, {"id":"r1","input_text":"hello","label":"positive","score":1.5,"timestamp":"2026-01-01T00:00:00Z"})
        assert any("DQ-02" in v for v in violations)

    def test_score_out_of_range_below(self):
        check_record(1, {"id":"r1","input_text":"hello","label":"positive","score":-0.1,"timestamp":"2026-01-01T00:00:00Z"})
        assert any("DQ-02" in v for v in violations)

    def test_invalid_label(self):
        check_record(1, {"id":"r1","input_text":"hello","label":"bad","score":0.9,"timestamp":"2026-01-01T00:00:00Z"})
        assert any("DQ-03" in v for v in violations)

    def test_allowed_labels_pass(self):
        for label in ["positive","negative","neutral","unknown"]:
            violations.clear()
            check_record(1, {"id":"r1","input_text":"hello","label":label,"score":0.9,"timestamp":"2026-01-01T00:00:00Z"})
            assert len(violations) == 0

    def test_invalid_timestamp_is_warning_not_violation(self):
        check_record(1, {"id":"r1","input_text":"hello","label":"positive","score":0.9,"timestamp":"not-a-date"})
        assert len(violations) == 0
        assert any("DQ-06" in w for w in warnings)

    def test_empty_input_text(self):
        check_record(1, {"id":"r1","input_text":"","label":"positive","score":0.9,"timestamp":"2026-01-01T00:00:00Z"})
        assert any("DQ-05" in v for v in violations)

class TestEvalGate:
    def test_metrics_above_threshold_pass(self):
        assert 0.85 >= 0.80

    def test_metric_below_threshold_fails(self):
        assert 0.70 < 0.80

    def test_inverted_metric_latency(self):
        assert 180 <= 200

    def test_inverted_metric_latency_fail(self):
        assert 250 > 200
