# Task: Bridge Desktop → Web UI

Replace the CustomTkinter GUI with the web UI from `../AdaptusMechanicusTranslator-Web/`.
**The desktop app is the reference** — all features and behaviors it has must be preserved.
The web UI is a draft/mockup and can be freely modified to match the desktop behavior.
`translator.py` and its tests are untouched throughout.

---

## 1 — Add Flask dependency

In `pyproject.toml`, add `flask` to the main dependencies.

---

## 2 — Create `server.py`

Flask app with two routes:

**`GET /`** — serve `index.html` from `../AdaptusMechanicusTranslator-Web/index.html` as a static file.

**`POST /translate`** — SSE endpoint. Accepts JSON body:
```json
{ "text": "...", "persona": "tech_priest|skitarii", "mode": "reformulate|litany", "input_lang": "english|french" }
```

Streams SSE events:
- `event: en` / `data: <json-encoded token>` — for each English output token
- `event: fr` / `data: <json-encoded token>` — for each French output token
- `event: done` / `data: {}` — when finished

Translation logic (always produces both EN and FR):
1. If `input_lang == "french"`: call `translate_to_english(text)` (blocking) to get `en_input`; otherwise `en_input = text`
2. Stream `translate_stream(en_input, persona, "english", mode)` — collect tokens, emit as `event: en`
3. Stream `translate_to_french_stream("".join(en_tokens))` — emit as `event: fr`

Use `flask.stream_with_context` + `Response(..., content_type="text/event-stream")`.

---

## 3 — Create `app.py`

Entry point that starts the server and opens the browser:

```python
import threading, webbrowser
from server import app

if __name__ == "__main__":
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
```

---

## 4 — Update `index.html`

Four changes to the JavaScript in `../AdaptusMechanicusTranslator-Web/index.html`:

**a) Remove the demo note** — delete the `<div class="demo-note">` block (the "MOCKUP — BACKEND NON CONNECTÉ" banner).

**b) Update status bar text** — change the static `"MISTRAL 7B — OMNISSIAH APPROVED — GPU ACTIVE"` to `"CONNECTING TO MACHINE SPIRIT..."`, then after a `fetch('/health')` or first successful translate, update it to `"MISTRAL 7B — OMNISSIAH APPROVED"`. (Keep it simple: static "MACHINE SPIRIT ACTIVE" on load is acceptable.)

**c) Replace `transmute()`** — remove the mock response logic and fake delay. Call the real API using `fetch` + `ReadableStream`:

```js
const resp = await fetch('/translate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: input, persona: currentPersona, mode: currentMode, input_lang: currentLang })
});

// Show output section, clear panels, add streaming cursor
outputSection.style.display = 'block';
const enEl = document.getElementById('enOutput');
const frEl = document.getElementById('frOutput');
enEl.textContent = ''; enEl.classList.add('streaming');
frEl.textContent = ''; frEl.classList.add('streaming');

// Parse SSE from response.body
const reader = resp.body.getReader();
const decoder = new TextDecoder();
let buf = '';
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buf += decoder.decode(value, { stream: true });
  const parts = buf.split('\n\n');
  buf = parts.pop();
  for (const block of parts) {
    const eventLine = block.match(/^event: (\w+)/m);
    const dataLine  = block.match(/^data: (.+)/m);
    if (!eventLine || !dataLine) continue;
    const token = JSON.parse(dataLine[1]);
    if (eventLine[1] === 'en') enEl.textContent += token;
    if (eventLine[1] === 'fr') frEl.textContent += token;
    if (eventLine[1] === 'done') { enEl.classList.remove('streaming'); frEl.classList.remove('streaming'); }
  }
}
```

**d) Remove `streamText()` and `mockResponses`** — they are replaced by the above.

---

## 5 — Update `README.md`

Replace the "USAGE" section to reflect the new entry point:

```bash
uv run python app.py    # starts server + opens browser at http://localhost:5000
```

Keep CLI and test sections unchanged. Remove the CustomTkinter launch instructions.

---

## Done state

- `uv run python app.py` opens the browser UI backed by real Mistral inference
- `uv run python cli.py "text"` still works as before
- `uv run pytest` still passes
- `mechanicus_translator.py` can be deleted once the above is verified working
