# Code Bank Workflow

A Python desktop learning application designed to help developers master code snippets through structured active recall, the Feynman technique, Notion database synchronization, and AI-powered code explanations.

[![CI](https://github.com/bmotana/code-bank-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/bmotana/code-bank-workflow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

Retaining programming concepts and syntax requires deliberate practice. **Code Bank Workflow** bridges the gap between snippet storage and muscle memory by combining:

- **Notion as a Personal Snippet Vault**: Pulls code exercises directly from your Notion workspace with seamless offline fallback support.
- **Active Recall Practice**: Challenge yourself to reproduce code line-by-line and level-by-level under timed or obscured display modes.
- **Feynman Technique Explanations**: Cement your understanding by explaining complex snippets in plain English.
- **AI-Powered Code Analysis**: Generate deep explanations, edge-case breakdowns, and pedagogical walk-throughs using Hugging Face (DeepSeek, LLaMA) or Google Gemini.

---

## Features

### Available Now
- 🖥️ **Interactive Desktop GUI**: Built with Tkinter, featuring a modular multi-page interface (Home, Recall Game, Feynman Technique, and Settings).
- 🧠 **Recall Practice Game**: Progressive recall challenges with real-time Pygments syntax highlighting and line numbering.
- ✍️ **Feynman Study Studio**: Interactive workspace to write, review, and refine code concept explanations.
- 🔄 **Notion Integration & Offline Resilience**: Connects to your Notion Code Bank database. If credentials or network connectivity are missing, the app gracefully falls back to built-in sample algorithms (such as Bubble Sort).
- 🤖 **AI-Assisted Explanations**: Plug in Hugging Face Inference (`DeepSeek-R1-Distill-Qwen-32B`, `Llama-3.3-70B-Instruct`) or Google Gemini for automatic snippet breakdown.
- 🎨 **Customizable Interface**: Dark/light theme toggles, configurable font sizes, and auto-save options.

### Roadmap
- 🗂️ **Anki Flashcard Export**: Automated export of snippets into `.apkg` decks for spaced repetition.
- 📈 **Longitudinal Progress Tracking**: Granular mastery statistics and multi-stage retention metrics across practice sessions.

---

## Project Architecture

```
code-bank-workflow/
├── config/
│   ├── default_config.yaml      # Model endpoints, Notion base URLs, and Anki defaults
│   └── stage_definitions.yaml   # Learning stage configurations
├── docs/                        # Detailed setup, user guide, and API documentation
├── src/
│   ├── core/                    # Snippet management, caching, and progress tracker stubs
│   │   ├── cache_handler.py
│   │   ├── progress_tracker.py
│   │   └── snippet_manager.py
│   ├── gui/                     # Desktop interface (Tkinter)
│   │   ├── home_page.py         # Home, Recall Game, Feynman, and Settings views
│   │   ├── main_window.py       # Main application container and navigation router
│   │   └── widgets/             # Code editor and snippet card components
│   ├── integrations/            # External service clients
│   │   ├── anki_exporter.py     # Flashcard export module
│   │   ├── fallback_handler.py  # Offline and error fallback logic
│   │   ├── gemini_client.py     # Google Gemini GenAI integration
│   │   ├── hg_client.py         # Hugging Face Inference API integration
│   │   └── notion_client.py     # Notion API client and snippet extractor
│   └── utils/                   # Config loading, syntax highlighting, and helpers
└── tests/                       # Unit and integration test suite
```

---

## Quick Start

### 1. Prerequisites

- **Python**: Version 3.8 to 3.13.
- **Tkinter**: Included with standard Python on Windows and macOS. On Linux (Ubuntu/Debian), install via:
  ```bash
  sudo apt-get install python3-tk
  ```

### 2. Clone and Setup Environment

```bash
# Clone repository
git clone https://github.com/bmotana/code-bank-workflow.git
cd code-bank-workflow

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Install dependencies (portable contributor set)
pip install -r requirements-ci.txt
pip install -e .
```

> [!NOTE]
> `requirements-ci.txt` provides cross-platform dependencies for development and testing. `requirements.txt` contains a full frozen local environment.

### 3. Configure Secrets

Create your `.env` configuration file from the provided template:

```bash
# Linux / macOS:
cp .env.example .env

# Windows (PowerShell):
Copy-Item .env.example .env

# Windows (CMD):
copy .env.example .env
```

Edit `.env` with your API credentials (all keys are optional; the application uses built-in fallbacks when keys are omitted):

```dotenv
# API Keys (Optional)
HF_API_TOKEN=your_hugging_face_token_here
GEMINI_API_KEY=your_gemini_api_key_here
NOTION_API_TOKEN=your_notion_api_token_here

# Notion Database IDs (Optional)
CODEBANK_DATABASE_ID=your_notion_database_id_here
TEST_DATABASE_ID=your_test_database_id_here
```

### 4. Run the Application

Launch the desktop GUI:

```bash
python -m src.gui.main_window
```

---

## Notion Database Setup

When connecting your own Notion database, ensure your database has the following properties:

| Property Name | Property Type | Description |
| :--- | :--- | :--- |
| **Code Description** | Title | Name / summary of the snippet |
| **Status** | Status / Select | Progress state (`Not started`, `In progress`, `Done`) |

The snippet code itself should be formatted inside a code block within the page content.

---

## Configuration

Default models and service URLs are configured in [`config/default_config.yaml`](config/default_config.yaml):

```yaml
notion:
  base_url: "https://api.notion.com/v1"
  codebank_url: "https://www.notion.so/your-workspace/your-database-id"
  headers:
    Content-Type: "application/json"
    Notion-Version: "2022-06-28"

huggingface:
  base_url: "https://api-inference.huggingface.co/models"
  default_model: "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
  models:
    deepseek: "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
    llama: "meta-llama/HgClient-3.3-70B-Instruct"

gemini:
  websites:
    main_website: "https://app.gemini.com/chat"
    website_2: "https://aistudio.google.com/app/apikey"
```

---

## Development & Testing

### Linting

Code style is enforced using `flake8` according to rules in [`.flake8`](.flake8):

```bash
flake8 src tests
```

### Running Tests

```bash
# Run unit and integration tests
pytest tests/ -v
```

CI runs automatically on push and pull requests to `main` across Linux environments with virtual display (`xvfb`). See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## Documentation

- [Setup Guide](docs/setup.md)
- [User Guide](docs/user_guide.md)
- [API Reference](docs/api.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
