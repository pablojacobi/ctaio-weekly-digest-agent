.PHONY: run test lint check

run:
	python3 main.py

test:
	python3 -m pytest -q

lint:
	ruff check .

check: lint test
