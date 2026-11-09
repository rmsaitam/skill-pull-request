.PHONY: setup test coverage validate check

setup:
	uv venv
	uv pip install pytest pytest-cov

test:
	uv run --with pytest --with pytest-cov pytest -q

coverage:
	uv run --with pytest --with pytest-cov pytest --cov-branch --cov=scripts --cov=skills/pr/scripts --cov-report=term-missing --cov-fail-under=80

validate:
	python3 scripts/validate_plugin.py .

check: coverage validate
