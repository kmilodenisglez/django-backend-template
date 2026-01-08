#!/usr/bin/env bash
set -euo pipefail

# Wrapper to run pytest using the project's Poetry virtualenv when available.
# Falls back to `poetry run pytest` if the venv path isn't found, then to system pytest.

ARGS=("$@")

# Priority order to determine what tests to run:
# 1. If args are provided to the script, use them (manual override).
# 2. If PRE_COMMIT_TESTS is set, run that subset and disable pytest-django plugin.
# 3. Otherwise run pytest with any provided args (empty -> full suite).

if [ ${#ARGS[@]} -gt 0 ]; then
  PYTEST_ARGS=("${ARGS[@]}")
elif [ -n "${PRE_COMMIT_TESTS:-}" ]; then
  # For pre-commit quick-run we prefer a fast subset and avoid importing Django
  PYTEST_ARGS=("-q" "-p" "no:django" ${PRE_COMMIT_TESTS})
else
  PYTEST_ARGS=()
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
