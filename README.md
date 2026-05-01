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
- [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) (for remote access)
- A GPU is recommended but not required

---

## INSTALLATION

```bash
uv sync
```

---

## USAGE — LOCAL

```bash
uv run python app.py
```

Opens the browser at `http://localhost:5000` automatically.

---

## USAGE — SHARE WITH FRIENDS

```bash
uv run python share.py
```

Starts the server and a Cloudflare tunnel together. Prints the URL as soon as it's ready — send it to friends along with the Vercel URL.

On the Vercel page, they scroll to **COGITATOR LINK**, paste the tunnel URL, click **CONNECT**.

---

## LICENSE

MIT — see [LICENSE](LICENSE).

---

*Fan creation. Not affiliated with or endorsed by Games Workshop. Warhammer 40,000 and Adeptus Mechanicus are trademarks of Games Workshop Ltd.*
