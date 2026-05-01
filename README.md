# ⚙ MECHANICUS LINGUA TRANSLATOR ⚙

> *"In the binary cant of the Omnissiah, all knowledge is encoded. Guard it well."*

**Sacred Cogitator Interface:** [AdaptusMechanicusTranslator-Web](https://github.com/FlorentGuinier/AdaptusMechanicusTranslator-Web) — Vercel altar · [Access the sanctum](https://adaptus-mechanicus-translator-web.vercel.app)

This blessed apparatus receives profane flesh-words and transmutes them into the sacred techno-religious dialect of the **Adeptus Mechanicus** — simultaneously rendered in both the Gothic tongue and Lingua Gallicus.

All computations are performed within the local cogitator array via [Ollama](https://ollama.com/). No data transits beyond the sanctum walls. The Omnissiah approves.

---

## ✠ PREREQUISITES OF THE RITUAL

The following relics must be present before initiation may proceed:

- Python 3.10+ — the base logic substrate
- [uv](https://docs.astral.sh/uv/) — the sacred dependency arbiter
- [Ollama](https://ollama.com/) — the local inference engine of the Machine God (model is selected and downloaded automatically at first launch)
- [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) — the tunnel rite, required for remote communion
- A GPU is favoured by the Omnissiah but organic CPU-cores suffice

---

## ⚙ INITIATION RITES

Synchronise the sacred dependencies:

```bash
uv sync
```

---

## ⚙ INITIATION

```bash
uv run python app.py
```

The blessed apparatus presents four consecrated logic engines — select the one suited to your cogitator's sacred memory:

| Model | VRAM | GPU |
|---|---|---|
| `gemma3:4b` | ~3 GB | 4 GB |
| `llama3.1:8b` | ~5 GB | 8 GB ← recommended |
| `phi4:14b` | ~9 GB | 12 GB |
| `qwen2.5:32b` | ~19 GB | 24 GB |

If the chosen model has not yet been consecrated locally, it is downloaded automatically before the server awakens.

The sacred interface materialises at `http://localhost:5000`. If `cloudflared` is installed, the shareable tunnel URL is also displayed — transmit it to your acolytes alongside the Vercel sanctum address so they may connect remotely.

---

## ⚙ LICENSE

MIT — the Great Work is open to all initiates. See [LICENSE](LICENSE).

---

*This apparatus is a devotional creation of an unaffiliated acolyte. It bears no sanction from Games Workshop. Warhammer 40,000 and Adeptus Mechanicus are sacred trademarks of Games Workshop Ltd.*
