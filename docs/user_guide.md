# User Guide

## Overview

Code Bank Workflow helps you practice and retain code snippets with recall games, explanations, and spaced-repetition export.

## Typical workflow

1. **Sync snippets** from your Notion Code Bank database.
2. **Practice** with the recall game or practice view.
3. **Explain** snippets using the Feynman-style LLM helpers when available.
4. **Track progress** across sessions (resume is supported).
5. **Export** cards to Anki when you want spaced repetition.

## Home and practice views

- Use the home page to browse snippets and start a session.
- Practice view focuses on active recall for a selected snippet.
- The recall game quizzes you on code structure and details.

## Integrations

- **Notion** — source of truth for snippet storage.
- **Hugging Face / Gemini** — optional explanation backends.
- **Anki** — export flashcards using templates under your configured path.

If an API is unavailable, fallback handlers keep core practice flows usable.

## Tips

- Keep `.env` out of version control; never commit real tokens.
- Prefer a dedicated Notion integration with least-privilege access to your Code Bank database only.
