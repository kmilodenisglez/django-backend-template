# Contributing

Thank you for contributing to Isowo! This short guide helps you set up a local development environment, follow the project's style rules, and submit high-quality pull requests.

## Developer setup

1. Install dependencies (Poetry recommended):

```bash
poetry install --no-interaction --no-ansi
```

2. Initialize developer tooling and hooks:

```bash
make bootstrap
make install-pre-commit
```

3. Apply formatting and linting locally:

```bash
make format
make lint
```

4. Run tests:

```bash
make test
```

## Working on changes

- Create a new branch per feature or bugfix: `git checkout -b feature/my-feature`
- Keep commits small and focused. Use descriptive commit messages.
- Run `make precommit-all` to apply hooks to all files before opening a PR.

## Pull request checklist

- [ ] Tests added or updated for new behavior
- [ ] All checks pass (Ruff, pre-commit hooks, pytest)
- [ ] Documentation updated if necessary

## Style & tooling

- Ruff is used for linting and formatting. Use `make format` and `make lint` locally.
- Pre-commit hooks run Ruff on commit and prevent common issues (trailing whitespace, missing final newline, large files).
