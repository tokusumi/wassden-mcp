.PHONY: format lint typecheck test check ci help

# Individual commands
format:
	uv run ruff format

lint:
	uv run ruff check

typecheck:
	uv run mypy wassden

test:
	uv run pytest --cov=wassden

# Composite commands
check: format lint typecheck test
	@echo "✅ All checks passed!"

ci:
	uv run ruff format --check
	uv run ruff check
	uv run mypy wassden
	uv run pytest --cov=wassden
	@echo "✅ All CI checks passed!"

help:
	@echo "Available commands:"
	@echo "  format    - Format code with ruff"
	@echo "  lint      - Lint code with ruff"
	@echo "  typecheck - Type check with mypy"
	@echo "  test      - Run tests with coverage"
	@echo "  check     - Run format, lint, typecheck, and test with coverage"
	@echo "  ci        - Run CI checks (format --check, lint, typecheck, test with coverage)"