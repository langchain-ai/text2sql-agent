# Makefile for Project Automation

.PHONY: install lint test build all clean security-scan format

# Variables
PACKAGE_NAME = agents
TEST_DIR = tests

# Default target
all: lint test

# Install project dependencies
install:
	uv sync

# Linting and Formatting Checks
lint:
	uv run ruff check $(PACKAGE_NAME) $(TEST_DIR)
	uv run black --check $(PACKAGE_NAME) $(TEST_DIR)
	uv run isort --check-only $(PACKAGE_NAME) $(TEST_DIR)

# Run Tests with Coverage
test:
	uv run pytest --cov=$(PACKAGE_NAME) --cov-report=xml $(TEST_DIR)/

# Run Pre-Commit Hooks
pre-commit:
	uv run pre-commit run --all-files

# Format Code (auto-fix)
format:
	uv run black $(PACKAGE_NAME) $(TEST_DIR)
	uv run isort $(PACKAGE_NAME) $(TEST_DIR)
	uv run ruff check --fix $(PACKAGE_NAME) $(TEST_DIR)

# Security Scanning
security-scan:
	uv run bandit -r $(PACKAGE_NAME)/

# Clean Up Generated Files
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .langgraph_api/
	rm -rf .coverage*
	rm -rf *.coverage.*
	rm -rf coverage.xml
	rm -rf evaluation_config__*.json

# Build the Package
build:
	uv run build
