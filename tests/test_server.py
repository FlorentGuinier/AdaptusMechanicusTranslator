"""
Unit tests for server.py — Flask routes, no live Ollama connection required.
"""
import json
import pytest
from unittest.mock import MagicMock, patch

from server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _parse_sse(data: bytes) -> list[dict]:
    """Parse a raw SSE response body into a list of {event, data} dicts."""
    events = []
    current = {}
    for line in data.decode().splitlines():
        if line.startswith("event:"):
            current["event"] = line[len("event:"):].strip()
        elif line.startswith("data:"):
            current["data"] = line[len("data:"):].strip()
        elif line == "" and current:
            events.append(current)
            current = {}
    if current:
        events.append(current)
    return events


def _make_list_response(*names: str) -> MagicMock:
    models = []
    for name in names:
        m = MagicMock()
        m.model = name
        m.name = name
        models.append(m)
    resp = MagicMock()
    resp.models = models
    return resp


# ── GET / ──────────────────────────────────────────────────────────────────────

def test_index_returns_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"<!DOCTYPE html>" in r.data or b"<!doctype html>" in r.data.lower()


# ── GET /status ────────────────────────────────────────────────────────────────

def test_status_ok_when_mistral_present(client):
    with patch("server.ollama.list", return_value=_make_list_response("mistral:latest")):
        r = client.get("/status")
    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_status_false_when_no_mistral(client):
    with patch("server.ollama.list", return_value=_make_list_response("llama3", "phi3")):
        r = client.get("/status")
    assert r.get_json()["ok"] is False


def test_status_false_when_ollama_unreachable(client):
    with patch("server.ollama.list", side_effect=Exception("connection refused")):
        r = client.get("/status")
    assert r.get_json()["ok"] is False


def test_status_partial_name_match(client):
    with patch("server.ollama.list", return_value=_make_list_response("mistral:7b-instruct-q4_0")):
        r = client.get("/status")
    assert r.get_json()["ok"] is True


def test_status_returns_ok_key(client):
    with patch("server.ollama.list", side_effect=Exception):
        r = client.get("/status")
    assert "ok" in r.get_json()


# ── POST /translate — content type and structure ───────────────────────────────

def test_translate_content_type_is_sse(client):
    with patch("server.translate_stream", return_value=iter(["x"])), \
         patch("server.translate_to_french_stream", return_value=iter(["y"])):
        r = client.post("/translate", json={"text": "test", "input_lang": "english"})
    assert "text/event-stream" in r.content_type


def test_translate_emits_done_event(client):
    with patch("server.translate_stream", return_value=iter(["a"])), \
         patch("server.translate_to_french_stream", return_value=iter(["b"])):
        r = client.post("/translate", json={"text": "test", "input_lang": "english"})
        data = r.data  # consume stream while patches are active
    events = _parse_sse(data)
    assert any(e["event"] == "done" for e in events)


def test_translate_done_event_is_last(client):
    with patch("server.translate_stream", return_value=iter(["a"])), \
         patch("server.translate_to_french_stream", return_value=iter(["b"])):
        r = client.post("/translate", json={"text": "test", "input_lang": "english"})
        data = r.data
    events = _parse_sse(data)
    assert events[-1]["event"] == "done"


def test_translate_en_events_before_fr_events(client):
    with patch("server.translate_stream", return_value=iter(["en_tok"])), \
         patch("server.translate_to_french_stream", return_value=iter(["fr_tok"])):
        r = client.post("/translate", json={"text": "test", "input_lang": "english"})
        data = r.data
    types = [e["event"] for e in _parse_sse(data)]
    assert types.index("en") < types.index("fr")


def test_translate_tokens_are_json_encoded(client):
    with patch("server.translate_stream", return_value=iter(['has "quotes" & chars'])), \
         patch("server.translate_to_french_stream", return_value=iter(["fr"])):
        r = client.post("/translate", json={"text": "test", "input_lang": "english"})
        data = r.data
    en_events = [e for e in _parse_sse(data) if e["event"] == "en"]
    assert json.loads(en_events[0]["data"]) == 'has "quotes" & chars'


# ── POST /translate — English input ───────────────────────────────────────────

def test_translate_english_streams_correct_en_tokens(client):
    with patch("server.translate_stream", return_value=iter(["Praise ", "the Omnissiah"])), \
         patch("server.translate_to_french_stream", return_value=iter(["Louez"])):
        r = client.post("/translate", json={"text": "hello", "input_lang": "english"})
        data = r.data
    en_tokens = [json.loads(e["data"]) for e in _parse_sse(data) if e["event"] == "en"]
    assert en_tokens == ["Praise ", "the Omnissiah"]


def test_translate_english_streams_correct_fr_tokens(client):
    with patch("server.translate_stream", return_value=iter(["Praise"])), \
         patch("server.translate_to_french_stream", return_value=iter(["Louez ", "l'Omnimessie"])):
        r = client.post("/translate", json={"text": "hello", "input_lang": "english"})
        data = r.data
    fr_tokens = [json.loads(e["data"]) for e in _parse_sse(data) if e["event"] == "fr"]
    assert fr_tokens == ["Louez ", "l'Omnimessie"]


def test_translate_english_does_not_call_translate_to_english(client):
    with patch("server.translate_stream", return_value=iter(["x"])), \
         patch("server.translate_to_french_stream", return_value=iter(["y"])), \
         patch("server.translate_to_english") as mock_en:
        client.post("/translate", json={"text": "hi", "input_lang": "english"})
    mock_en.assert_not_called()


def test_translate_english_passes_text_directly_to_translate_stream(client):
    with patch("server.translate_stream", return_value=iter(["x"])) as mock_ts, \
         patch("server.translate_to_french_stream", return_value=iter(["y"])):
        client.post("/translate", json={"text": "my flesh words", "input_lang": "english"})
    assert mock_ts.call_args.args[0] == "my flesh words"


# ── POST /translate — French input ────────────────────────────────────────────

def test_translate_french_calls_translate_to_english(client):
    with patch("server.translate_to_english", return_value="hello") as mock_en, \
         patch("server.translate_stream", return_value=iter(["x"])), \
         patch("server.translate_to_french_stream", return_value=iter(["y"])):
        client.post("/translate", json={"text": "bonjour", "input_lang": "french"})
    mock_en.assert_called_once_with("bonjour")


def test_translate_french_passes_english_result_to_translate_stream(client):
    with patch("server.translate_to_english", return_value="translated"), \
         patch("server.translate_stream", return_value=iter(["x"])) as mock_ts, \
         patch("server.translate_to_french_stream", return_value=iter(["y"])):
        client.post("/translate", json={"text": "bonjour", "input_lang": "french"})
    assert mock_ts.call_args.args[0] == "translated"


# ── POST /translate — persona and mode passthrough ────────────────────────────

def test_translate_passes_persona_to_translate_stream(client):
    with patch("server.translate_stream", return_value=iter(["x"])) as mock_ts, \
         patch("server.translate_to_french_stream", return_value=iter(["y"])):
        client.post("/translate", json={"text": "t", "persona": "skitarii", "input_lang": "english"})
    assert mock_ts.call_args.args[1] == "skitarii"


def test_translate_passes_mode_to_translate_stream(client):
    with patch("server.translate_stream", return_value=iter(["x"])) as mock_ts, \
         patch("server.translate_to_french_stream", return_value=iter(["y"])):
        client.post("/translate", json={"text": "t", "mode": "litany", "input_lang": "english"})
    assert mock_ts.call_args.args[3] == "litany"


def test_translate_passes_collected_en_to_french_stream(client):
    with patch("server.translate_stream", return_value=iter(["The ", "Machine ", "God"])), \
         patch("server.translate_to_french_stream") as mock_fr:
        mock_fr.return_value = iter(["Le Dieu-Machine"])
        r = client.post("/translate", json={"text": "test", "input_lang": "english"})
        _ = r.data  # force generator consumption before patches are released
    mock_fr.assert_called_once_with("The Machine God")


def test_translate_defaults_to_tech_priest_persona(client):
    with patch("server.translate_stream", return_value=iter(["x"])) as mock_ts, \
         patch("server.translate_to_french_stream", return_value=iter(["y"])):
        client.post("/translate", json={"text": "t", "input_lang": "english"})
    assert mock_ts.call_args.args[1] == "tech_priest"


def test_translate_defaults_to_reformulate_mode(client):
    with patch("server.translate_stream", return_value=iter(["x"])) as mock_ts, \
         patch("server.translate_to_french_stream", return_value=iter(["y"])):
        client.post("/translate", json={"text": "t", "input_lang": "english"})
    assert mock_ts.call_args.args[3] == "reformulate"
