**Local contributor guide — pre-commit & tests**

This short guide explains how to run the project's pre-commit hooks and configure the quick test subset used during commits.

1. Copy example env and adjust locally (do not commit your `.env`):

```bash
cp .env.example .env
# edit .env as needed
```

2. Install development tools (recommended via Poetry):

```bash
poetry install
```

3. Install `pre-commit` hooks:

```bash
pip install pre-commit
pre-commit install
```

4. By default the pre-commit pytest hook will run the subset set in `PRE_COMMIT_TESTS`.
   The default value is `apps/core/tests` (fast unit tests). To run that subset
   during the current shell session, either export the variable or source your `.env`:

```bash
export PRE_COMMIT_TESTS=apps/core/tests
# or
set -o allexport; source .env; set +o allexport
pre-commit run --all-files
```

5. If you want pre-commit to run the full test suite on commit, unset `PRE_COMMIT_TESTS`.

Notes
- The repository includes `scripts/run-tests.sh` used by the pre-commit hook. It will
  try to run `pytest` from the Poetry-managed virtualenv if available, falling back to
  `poetry run pytest` or system `pytest`.
- Keep the pre-commit test subset small to keep commit-time checks fast. Use CI for
  full test coverage on PRs.
