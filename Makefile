.PHONY: test data-check eval-gate install lint

install:
	pip install -r requirements.txt

lint:
	python -m flake8 src/ tests/ --max-line-length=120 --ignore=E501

test:
	python -m pytest tests/ -v --ignore=tests/test_data_checks.py --ignore=tests/test_eval_gate.py

data-check:
	python -m pytest tests/test_data_checks.py -v

eval-gate:
	python -m pytest tests/test_eval_gate.py -v
