#!/usr/bin/env bash
set -euo pipefail

# Wrapper to run pytest using the project's Poetry virtualenv when available.
# Falls back to `poetry run pytest` if the venv path isn't found, then to system pytest.

ARGS=("$@")

# Ensure PYTHONPATH and DJANGO_SETTINGS_MODULE are set so pre-commit can run
# without requiring the caller to export them (makes hooks robust in editors).
export PYTHONPATH="${PYTHONPATH:-$PWD}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings}"

# Priority order to determine what tests to run:
# 1. If args are provided to the script, use them (manual override).
# 2. If PRE_COMMIT_TESTS is set in the environment, run that subset and disable pytest-django plugin.
# 3. If PRE_COMMIT_TESTS is not set, try to read it from `.env` or `.env.example`.
# 4. Otherwise run pytest with any provided args (empty -> full suite).

if [ ${#ARGS[@]} -gt 0 ]; then
  PYTEST_ARGS=("${ARGS[@]}")
else
  # If PRE_COMMIT_TESTS isn't set in the environment, try .env then .env.example
  if [ -z "${PRE_COMMIT_TESTS:-}" ]; then
    # Try to parse PRE_COMMIT_TESTS from .env (don't source to avoid executing arbitrary content)
    if [ -f .env ]; then
      val=$(grep -E '^PRE_COMMIT_TESTS=' .env | head -n1 | cut -d'=' -f2-)
      if [ -n "$val" ]; then
        PRE_COMMIT_TESTS="$val"
      fi
    fi
    # If still empty, fall back to .env.example
    if [ -z "${PRE_COMMIT_TESTS:-}" ] && [ -f .env.example ]; then
      val=$(grep -E '^PRE_COMMIT_TESTS=' .env.example | head -n1 | cut -d'=' -f2-)
      if [ -n "$val" ]; then
        PRE_COMMIT_TESTS="$val"
      fi
    fi
  fi

  if [ -n "${PRE_COMMIT_TESTS:-}" ]; then
    # For pre-commit quick-run we prefer a fast subset. Do not disable the
    # pytest-django plugin here so Django tests (marked with django_db) run
    # correctly during pre-commit checks.
    PYTEST_ARGS=("-q" ${PRE_COMMIT_TESTS})
  else
    PYTEST_ARGS=()
  fi
fi

if command -v poetry >/dev/null 2>&1; then
  VENV_PATH=$(poetry env info -p 2>/dev/null || true)
  if [ -n "$VENV_PATH" ] && [ -x "$VENV_PATH/bin/pytest" ]; then
    exec "$VENV_PATH/bin/pytest" "${PYTEST_ARGS[@]}"
  else
    exec poetry run pytest "${PYTEST_ARGS[@]}"
  fi
else
  exec pytest "${PYTEST_ARGS[@]}"
fi
