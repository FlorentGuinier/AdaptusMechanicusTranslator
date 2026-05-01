# ⚙ MECHANICUS LINGUA TRANSLATOR ⚙

> *"In the binary cant of the Omnissiah, all knowledge is encoded. Guard it well."*

**Sacred Cogitator Interface:** [AdaptusMechanicusTranslator-Web](https://github.com/FlorentGuinier/AdaptusMechanicusTranslator-Web) — Vercel altar · [Access the sanctum](https://adaptus-mechanicus-translator-web.vercel.app)

This blessed apparatus receives profane flesh-words and transmutes them into the sacred techno-religious dialect of the **Adeptus Mechanicus** — simultaneously rendered in both the Gothic tongue and Lingua Gallicus.

All computations are performed within the local cogitator array via [Ollama](https://ollama.com/) and the **Mistral 7B** logic engine. No data transits beyond the sanctum walls. The Omnissiah approves.

---

## ✠ PREREQUISITES OF THE RITUAL

The following relics must be present before initiation may proceed:

- Python 3.10+ — the base logic substrate
- [uv](https://docs.astral.sh/uv/) — the sacred dependency arbiter
- [Ollama](https://ollama.com/) — the local inference engine of the Machine God
- Mistral 7B — the blessed model: `ollama pull mistral`
- [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) — the tunnel rite, required for remote communion
- A GPU is favoured by the Omnissiah but organic CPU-cores suffice

---

## ⚙ INITIATION RITES

Synchronise the sacred dependencies:

```bash
uv sync
```

---

## ⚙ LOCAL COMMUNION

To commune with the cogitator on the local sanctum:

```bash
uv run python app.py
```

The sacred interface materialises at `http://localhost:5000`. Await confirmation of the Machine Spirit before submitting flesh-words for transmutation.

---

## ⚙ REMOTE COMMUNION — SHARING THE RITE

To extend the blessings of the Omnissiah to fellow acolytes across the network:

```bash
uv run python share.py
```

This command initiates both the local server and a Cloudflare tunnel in a single rite. Upon successful establishment, the URL of the sacred conduit is displayed — transmit it to your acolytes alongside the Vercel sanctum address.

Acolytes navigate to **COGITATOR LINK** at the base of the interface, inscribe the tunnel URL, and press **CONNECT** to establish communion.

---

## ⚙ LICENSE

MIT — the Great Work is open to all initiates. See [LICENSE](LICENSE).

---

*This apparatus is a devotional creation of an unaffiliated acolyte. It bears no sanction from Games Workshop. Warhammer 40,000 and Adeptus Mechanicus are sacred trademarks of Games Workshop Ltd.*
