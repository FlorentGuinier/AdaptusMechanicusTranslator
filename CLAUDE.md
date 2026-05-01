# AdaptusMechanicusTranslator — Project Context

## What this project is

A Warhammer 40K-themed text reformulator running entirely locally via Ollama + Mistral 7B.

**Source files:**
- `translator.py` — core logic: prompts, `translate_stream`, `translate_to_english`, `translate_to_french_stream`, `get_inference_device`
- `mechanicus_translator.py` — CustomTkinter desktop GUI
- `cli.py` — CLI for fast iteration
- `tests/test_translator.py` — unit tests (all mocked, no live Ollama needed)

## Sibling project: AdaptusMechanicusTranslator-Web

Located at `../AdaptusMechanicusTranslator-Web/`. Live at https://adaptus-mechanicus-translator-web.vercel.app/ — a static single-file web UI (`index.html`) with no backend, currently using hardcoded mock responses. It has the same features (personas, modes, language selector) and a more polished mobile-friendly aesthetic, but it is a **draft/mockup**. It can be freely modified to match the desktop app's behavior.

## Goal

**Replace the CustomTkinter GUI (`mechanicus_translator.py`) with the web UI.**

The plan is to:
1. Add a small local HTTP server (Flask or FastAPI) to this project that exposes `translator.py` as an API
2. Wire the web UI (`index.html`) to call that API instead of returning mock responses
3. The desktop app becomes: start the server, open the browser — no more CustomTkinter

`translator.py` and its tests are not affected. The GUI layer (`mechanicus_translator.py`) is what gets replaced.
