# AdaptusMechanicusTranslator — Project Context

## What this project is

A Warhammer 40K-themed text reformulator running entirely locally via Ollama.

**Source files:**
- `translator.py` — core logic: prompts, `translate_stream`, `translate_to_english`, `translate_to_french_stream`, `get_inference_device`
- `server.py` — Flask HTTP server: `GET /` serves the web UI, `GET /status` checks Ollama, `POST /translate` streams SSE (English then French tokens)
- `app.py` — entry point: interactive model selection (questionary), auto-pulls selected model if not present, starts Flask, opens browser, starts cloudflared tunnel if installed
- `tests/test_translator.py` — unit tests for translator.py (all mocked, no live Ollama needed)
- `tests/test_server.py` — unit tests for server.py (all mocked, no live Ollama needed)

## Sibling project: AdaptusMechanicusTranslator-Web

Located at `../AdaptusMechanicusTranslator-Web/`. Live at https://adaptus-mechanicus-translator-web.vercel.app/ — a static single-file web UI (`index.html`) that is the frontend for this server.

`server.py` serves `../AdaptusMechanicusTranslator-Web/index.html` directly at `GET /`.

## How to run

```bash
uv run python app.py
```

Presents a 4-option model selector (arrow keys), pulls the chosen model if needed, starts the server at `http://localhost:5000`, opens the browser, and starts a cloudflared tunnel if `cloudflared` is installed.

## Running tests

```bash
uv run python -m pytest tests/
```
