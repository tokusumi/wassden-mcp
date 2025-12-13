.PHONY: format lint typecheck test test-core test-dev test-ast check ci ci-core validate-examples help

# Individual commands
format:
	uv run --active ruff format

lint:
	uv run --active ruff check

typecheck:
	uv run --active mypy wassden

test:
	uv run --active pytest --cov=wassden

test-core:
	uv run --active pytest --cov=wassden -m "not dev"

test-dev:
	uv run --active pytest --cov=wassden -m "dev"

test-ast:
	USE_AST_VALIDATION=1 uv run --active pytest tests/unit/test_spec_ast/ tests/unit/test_validate.py -v

validate-examples:
	uv run --active pytest tests/integration/test_spec_examples.py -v

# Composite commands
check: format lint typecheck test
	@scripts/verify-dev-cli.sh
	@echo "✅ All checks passed!"

ci:
	uv run ruff format --check
	uv run ruff check
	uv run mypy wassden
	USE_AST_VALIDATION=1 uv run pytest tests/unit/test_spec_ast/ tests/unit/test_validate.py -v
	uv run pytest --cov=wassden
	@scripts/verify-dev-cli.sh
	@echo "✅ CI checks passed!"

ci-core:
	uv run ruff format --check
	uv run ruff check
	uv run mypy wassden
	uv run pytest --cov=wassden -m "not dev"
	@scripts/verify-core-cli.sh
	@echo "✅ Core CI checks passed!"

help:
	@echo "Available commands:"
	@echo "  format          - Format code with ruff"
	@echo "  lint            - Lint code with ruff"
	@echo "  typecheck       - Type check with mypy"
	@echo "  test            - Run all tests with coverage"
	@echo "  test-core       - Run core tests only (no dev dependencies)"
	@echo "  test-dev        - Run dev tests only (requires dev dependencies)"
	@echo "  test-ast        - Run AST validation tests only"
	@echo "  check           - Run all checks with dev CLI verification (local dev)"
	@echo "  ci              - Run CI checks for dev mode"
	@echo "  ci-core         - Run CI checks for core functionality"
	@echo "  validate-examples - Run integration tests for spec examples (Japanese and English)"