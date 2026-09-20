# Setup Guide

## Requirements

- Python 3.8 or newer
- A Notion integration with access to your Code Bank database
- Optional: Hugging Face and/or Gemini API keys for LLM explanations

## Installation

1. Clone the repository and enter the project directory.
2. Create a virtual environment and activate it.
3. Install dependencies:

   ```bash
   # Full local environment (may include platform-specific packages)
   pip install -r requirements.txt
   pip install -e .

   # Or portable CI/contributor set:
   # pip install -r requirements-ci.txt && pip install -e .
   ```

4. Copy `.env.example` to `.env` and fill in your secrets:

   ```bash
   cp .env.example .env
   ```

5. Review `config/default_config.yaml` for Notion URLs, model defaults, and Anki settings.

## Running the app

```bash
python -m src.gui.main_window
```

## Running tests

```bash
pytest tests/ -v
```

Tests that call live APIs expect the corresponding environment variables (or GitHub Actions secrets in CI).

## Linting

```bash
flake8 src tests
```

Configuration is in `.flake8` at the repository root.
