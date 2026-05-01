# ⚙ MECHANICUS LINGUA TRANSLATOR ⚙

> *"Knowledge is power, guard it well."*

A Warhammer 40,000-themed text translator that reformulates any input into the sacred techno-religious language of the **Adeptus Mechanicus** — simultaneously in French and English.

Powered by [Ollama](https://ollama.com/) running **Mistral 7B** locally. No data leaves your machine. The Omnissiah approves.

---

## REQUIREMENTS — PREREQUISITES OF THE RITUAL

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- Mistral 7B model (auto-downloaded on first launch if not present)
- A GPU is recommended but not required (CPU mode works)

---

## INSTALLATION — INITIATION RITES

### Using `uv` (recommended)

```bash
uv sync
uv run python app.py
```

### Using `pip`

```bash
pip install flask ollama
python app.py
```

On first launch, if Mistral 7B is not already pulled, the app will download it automatically (~4 GB).

---

## USAGE — OPERATION OF THE SACRED COGITATOR

```bash
uv run python app.py
```

This starts the local server and opens the browser at `http://localhost:5000`.

1. Wait for the status bar to confirm the model is loaded
2. Select persona, mode, and input language
3. Enter your profane flesh-words in the input field
4. Click **TRANSMUTE TO BINARIC CANT**
5. Receive the blessed output in both English and French
6. Use the **COPY** buttons to copy each translation to clipboard

---

## CLI — FAST ITERATION WITHOUT THE GUI

Translate text directly from the terminal, tokens stream in real time:

```bash
uv run python cli.py "I need to sleep"
uv run python cli.py "I need to sleep" --persona skitarii
uv run python cli.py "cogitator" --mode litany
echo "The machine hungers" | uv run python cli.py
```

`--persona` accepts `tech_priest` (default) or `skitarii`. `--mode` accepts `reformulate` (default) or `litany`.

---

## DEVELOPMENT — RITES OF VERIFICATION

Install dev dependencies and run the test suite:

```bash
uv sync --group dev
uv run pytest
```

Tests cover the translation module (`translator.py`) in isolation — no live Ollama connection required, all ollama calls are mocked.

```bash
uv run pytest -v    # verbose output
uv run pytest -x    # stop on first failure
```

---

## PROJECT STRUCTURE

```
app.py                     # Entry point — starts server and opens browser
server.py                  # Flask server with SSE /translate endpoint
translator.py              # Core translation logic (no GUI dependency)
cli.py                     # Command-line interface for fast iteration
tests/
    test_translator.py     # Unit tests (all mocked)
pyproject.toml             # Project metadata and dependencies
../AdaptusMechanicusTranslator-Web/index.html   # Web UI (served by Flask)
```

---

## LICENSE

MIT — do whatever you want with this. See [LICENSE](LICENSE) for the full text.

---

*This project is a fan creation and is not affiliated with or endorsed by Games Workshop. Warhammer 40,000 and Adeptus Mechanicus are trademarks of Games Workshop Ltd.*
