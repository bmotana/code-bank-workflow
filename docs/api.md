# API Documentation

High-level module map for integrators and contributors. Prefer reading the source under `src/` for exact signatures.

## Package layout

| Package | Role |
| --- | --- |
| `src.gui` | Tkinter UI: main window, home page, practice view, recall game |
| `src.core` | Snippet management, progress tracking, caching |
| `src.integrations` | Notion, Hugging Face, Gemini, Anki, and fallbacks |
| `src.utils` | Config loading, file helpers, validation, highlighting |
| `config/` | YAML defaults and stage definitions |

## Integrations

### Notion (`src.integrations.notion_client`)

Reads and writes Code Bank pages via the Notion API using `NOTION_API_TOKEN` and database IDs from the environment / config.

### Hugging Face (`src.integrations.hg_client`)

Calls inference endpoints configured in `config/default_config.yaml` using `HF_API_TOKEN`.

### Gemini (`src.integrations.gemini_client`)

Uses `GEMINI_API_KEY` for generative explanations when HF is unavailable or not preferred.

### Anki (`src.integrations.anki_exporter`)

Exports flashcards using the deck name and template path from config.

## Configuration

- Environment: see `.env.example`
- Defaults: `config/default_config.yaml`
- Stages: `config/stage_definitions.yaml`

## Entry point

```bash
python -m src.gui.main_window
```
