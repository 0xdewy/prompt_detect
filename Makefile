# Makefile for Prompt Detective
# Uses uv for Python package management

.PHONY: help install dev test lint format typecheck build clean

# Default target
help:
	@echo "Prompt Detective Development Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make install    Install the package in development mode"
	@echo "  make dev        Install with development dependencies"
	@echo "  make test       Run tests"
	@echo "  make lint       Run linting checks"
	@echo "  make format     Format code with black"
	@echo "  make typecheck  Run type checking with mypy"
	@echo "  make build      Build package distribution"
	@echo "  make clean      Clean build artifacts"
	@echo "  make setup      Full development setup"
	@echo "  make pre-commit Run all checks before commit"
	@echo ""

# Install the package in development mode
install:
	uv pip install -e .

# Install with development dependencies
dev:
	uv pip install -e ".[dev]"

# Run tests
test:
	.venv-uv-new/bin/python -m pytest tests/ -v

# Run linting checks
lint:
	.venv-uv-new/bin/python -m ruff check prompt_detective/ scripts/ tests/

# Format code
format:
	.venv-uv-new/bin/python -m black prompt_detective/ scripts/ tests/

# Run type checking
typecheck:
	.venv-uv-new/bin/python -m mypy prompt_detective/

# Build package distribution
build:
	uv build

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Full development setup
setup: dev format lint test
	@echo "Development environment is ready!"

# Run all checks before commit
pre-commit: format lint typecheck test
	@echo "All checks passed!"