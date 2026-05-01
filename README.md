# MECHANICUS LINGUA TRANSLATOR

> *"Knowledge is power, guard it well."*

**Sibling repo:** [AdaptusMechanicusTranslator-Web](https://github.com/FlorentGuinier/AdaptusMechanicusTranslator-Web) — web UI (Vercel) · [Live demo](https://adaptus-mechanicus-translator-web.vercel.app)

A Warhammer 40,000-themed text translator that reformulates any input into the sacred techno-religious language of the **Adeptus Mechanicus** — simultaneously in English and French.

Powered by [Ollama](https://ollama.com/) running **Mistral 7B** locally. No data leaves your machine.

---

## REQUIREMENTS

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (package manager)
- [Ollama](https://ollama.com/) installed and running
- Mistral 7B pulled: `ollama pull mistral`
- A GPU is recommended but not required

---

## INSTALLATION

```bash
uv sync
```

---

## USAGE — LOCAL

Start the server and open the browser automatically:

```bash
uv run python app.py
```

The browser opens at `http://localhost:5000`.

1. Wait for the status bar to confirm the model is loaded
2. Select persona, mode, and input language
3. Enter text in the input field
4. Click **TRANSMUTE TO BINARIC CANT**
5. Use the **COPY** buttons to copy each translation

---

## USAGE — REMOTE (share with friends)

The web UI is also hosted on Vercel at:  
**https://adaptus-mechanicus-translator-web.vercel.app**

To let friends connect to your local server:

```bash
uv run python share.py
```

This starts the server and the tunnel together, and prints the URL to share as soon as it's ready.

Send friends the Vercel URL + the tunnel URL.  
On the Vercel page, they scroll to **COGITATOR LINK**, paste the URL, click **CONNECT**.

The URL is saved in their browser's localStorage — they only need to enter it once per ngrok session.

---

## CLI

Translate directly from the terminal:

```bash
uv run python cli.py "I need to sleep"
uv run python cli.py "I need to sleep" --persona skitarii
uv run python cli.py "cogitator" --mode litany
echo "The machine hungers" | uv run python cli.py
```

`--persona`: `tech_priest` (default) or `skitarii`  
`--mode`: `reformulate` (default) or `litany`

---

## DEVELOPMENT

```bash
uv sync
uv run python -m pytest
uv run python -m pytest -v    # verbose
uv run python -m pytest -x    # stop on first failure
```

All tests are mocked — no live Ollama connection required.

---

## PROJECT STRUCTURE

```
app.py                    # Entry point — starts server and opens browser
server.py                 # Flask API server (SSE streaming)
translator.py             # Core translation logic
cli.py                    # Command-line interface
tests/
    test_translator.py    # Unit tests for translator.py
    test_server.py        # Unit tests for server.py
pyproject.toml            # Dependencies (managed by uv)
../AdaptusMechanicusTranslator-Web/index.html   # Web UI
```

---

## LICENSE

MIT — see [LICENSE](LICENSE).

---

*Fan creation. Not affiliated with or endorsed by Games Workshop. Warhammer 40,000 and Adeptus Mechanicus are trademarks of Games Workshop Ltd.*
