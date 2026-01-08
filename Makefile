# Makefile for common developer tasks (Ruff formatting, linting & tests)
# Auto-detects Poetry. If Poetry is available, it will run tools inside Poetry's
# virtualenv (e.g. `poetry run ruff`). Otherwise it falls back to system tooling.

# Auto-detect poetry in PATH
POETRY := $(shell command -v poetry 2>/dev/null || true)
ifeq ($(POETRY),)
RUFF ?= ruff
PRE_COMMIT ?= pre-commit
PYTEST ?= pytest
else
RUFF ?= poetry run ruff
PRE_COMMIT ?= poetry run pre-commit
PYTEST ?= poetry run pytest
endif

.PHONY: help format lint fix ci test install-pre-commit

help:
	@echo "Makefile targets:"
	@echo "  format            -> run '$(RUFF) format .' to format code"
	@echo "  lint              -> run '$(RUFF) check .' to check for issues"
	@echo "  fix               -> run '$(RUFF) check --fix .' to auto-fix issues"
	@echo "  test              -> run unit tests (pytest)"
	@echo "  ci                -> run lint + tests"
	@echo "  install-pre-commit-> install pre-commit hooks (pre-commit must be installed)"
	@echo "  bootstrap         -> install project dev dependencies (poetry install)"
	@echo "  precommit-all     -> run pre-commit hooks against all files"

format:
	@echo "Running formatting..."
	$(RUFF) format .

lint:
	@echo "Running Ruff checks..."
	$(RUFF) check .

fix:
	@echo "Running Ruff auto-fix..."
	$(RUFF) check --fix .

test:
	@echo "Running tests..."
	$(PYTEST) -q

ci: lint test
	@echo "CI checks passed (ruff check + tests)."

install-pre-commit:
	@echo "Installing pre-commit hooks..."
	$(PRE_COMMIT) install
	@echo "pre-commit hooks installed. Run 'git add .' then commit to trigger hooks."

bootstrap:
	@echo "Bootstrapping development environment (poetry install if available)..."
	@if [ -n "$(POETRY)" ]; then \
		$(POETRY) install --no-interaction --no-ansi; \
		echo "Poetry dependencies installed."; \
	else \
		echo "Poetry not found. Please install poetry or run your package manager to install dev deps."; \
	fi

precommit-all:
	@echo "Running pre-commit hooks on all files..."
	$(PRE_COMMIT) run --all-files
