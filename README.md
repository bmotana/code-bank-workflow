# Code Bank Workflow

A learning system for mastering code snippets through structured recall practice, Notion sync, LLM explanations, and Anki export.

[![CI](https://github.com/bmotana/code-bank-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/bmotana/code-bank-workflow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features

- Interactive recall-based practice games
- Notion database integration for snippet management
- LLM-powered Feynman-style explanations (Hugging Face / Gemini)
- Anki flashcard export with customizable templates
- Progress tracking and session resume
- Fallback options when API dependencies are unavailable

## Quick start

```bash
# Clone
git clone git@github.com:bmotana/code-bank-workflow.git
cd code-bank-workflow

# Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install
pip install -r requirements.txt
pip install -e .

# Configure secrets
cp .env.example .env
# Edit .env with your API tokens and database IDs
```

Then launch the GUI:

```bash
python -m src.gui.main_window
```

Full setup details: [docs/setup.md](docs/setup.md)

## Configuration

| Variable | Description |
| --- | --- |
| `HF_API_TOKEN` | Hugging Face API token |
| `GEMINI_API_KEY` | Google Gemini API key |
| `NOTION_API_TOKEN` | Notion integration token |
| `CODEBANK_DATABASE_ID` | Notion Code Bank database ID |
| `TEST_DATABASE_ID` | Optional test database ID |

Defaults and model settings live in `config/default_config.yaml`.

## Development

```bash
# Portable lint/test deps (recommended for contributors / CI)
pip install -r requirements-ci.txt

# Lint
flake8 src tests

# Tests
pytest tests/ -v
```

Lint rules are defined in [`.flake8`](.flake8). CI runs lint and tests on every push/PR to `main` (see [`.github/workflows/ci.yml`](.github/workflows/ci.yml)). Use `requirements.txt` for a full local freeze; use `requirements-ci.txt` for cross-platform CI and contributor tooling.

## Documentation

- [Setup guide](docs/setup.md)
- [User guide](docs/user_guide.md)
- [API documentation](docs/api.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
