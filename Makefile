.PHONY: test data-check eval-gate slo-gate install

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v \
	  --ignore=tests/test_data_checks.py \
	  --ignore=tests/test_eval_gate.py \
	  --ignore=tests/test_slo_gate.py

data-check:
	python -m pytest tests/test_data_checks.py -v

eval-gate:
	python -m pytest tests/test_eval_gate.py -v

slo-gate:
	python -m pytest tests/test_slo_gate.py -v
