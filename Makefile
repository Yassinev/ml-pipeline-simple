.PHONY: test data-check eval-gate all

all: test data-check eval-gate

test:
	pytest tests/ -v --tb=short

data-check:
	python src/aispec/data_contract.py

eval-gate:
	python src/aispec/eval_gate.py
