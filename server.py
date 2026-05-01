import json
import logging
import time
from pathlib import Path

import ollama
from flask import Flask, Response, request, send_file, stream_with_context
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")

from translator import (PERSONA_TECH_PRIEST, PERSONA_CUSTOM, MODE_REFORMULATE,
                        translate_stream, translate_to_english,
                        translate_to_french_stream)

_INDEX = Path(__file__).parent.parent / "AdaptusMechanicusTranslator-Web" / "index.html"

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return send_file(_INDEX)


@app.route("/status")
def status():
    try:
        names = [getattr(m, "model", getattr(m, "name", "")) for m in ollama.list().models]
        return {"ok": bool(names)}
    except Exception:
        return {"ok": False}


@app.route("/translate", methods=["POST"])
def translate():
    data          = request.get_json(force=True)
    text          = data.get("text", "")
    persona       = data.get("persona", PERSONA_TECH_PRIEST)
    mode          = data.get("mode", MODE_REFORMULATE)
    input_lang    = data.get("input_lang", "english")
    custom_prompt = data.get("custom_prompt", "")

    logging.info("TRANSLATE  lang=%-7s persona=%-11s mode=%-11s chars=%d",
                 input_lang, persona, mode, len(text))
    t0 = time.monotonic()

    def generate():
        en_input = translate_to_english(text) if input_lang == "french" else text

        en_tokens = []
        for token in translate_stream(en_input, persona, "english", mode, custom_prompt):
            en_tokens.append(token)
            yield f"event: en\ndata: {json.dumps(token)}\n\n"

        for token in translate_to_french_stream("".join(en_tokens)):
            yield f"event: fr\ndata: {json.dumps(token)}\n\n"

        logging.info("DONE       %.1fs", time.monotonic() - t0)
        yield "event: done\ndata: {}\n\n"

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
