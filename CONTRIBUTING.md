# Contributing

Thanks for contributing to Code Bank Workflow.

## Getting started

1. Fork the repository and create a feature branch from `main`.
2. Follow [docs/setup.md](docs/setup.md) to install dependencies.
3. Copy `.env.example` to `.env` for local secrets (never commit `.env`).

## Development workflow

1. Make focused changes with clear intent.
2. Lint: `flake8 src tests`
3. Test: `pytest tests/ -v`
4. Open a pull request using the PR template.

## Code style

- Follow existing patterns in `src/` and `tests/`.
- Flake8 rules live in `.flake8`.
- Prefer type hints on new public functions.
- Keep commits small and messages descriptive.

## Issues

- Use the bug report template for defects.
- Use the feature request template for ideas.
- Search existing issues before opening a new one.

## Security

Do not open public issues for vulnerabilities. See [SECURITY.md](SECURITY.md).
