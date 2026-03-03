"""
Unit tests for translator.py — no GUI, no live Ollama connection required.
"""
import pytest
from unittest.mock import MagicMock, patch

import translator
from translator import (
    translate_stream, get_inference_device,
    MODEL_NAME, PERSONA_TECH_PRIEST, PERSONA_SKITARII,
    SYSTEM_PROMPT_TECH_PRIEST, SYSTEM_PROMPT_SKITARII,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_chunk(content: str) -> MagicMock:
    chunk = MagicMock()
    chunk.message.content = content
    return chunk


def _make_ps_response(model_name: str, size_vram: int) -> MagicMock:
    model = MagicMock()
    model.model = model_name
    model.name = model_name
    model.size_vram = size_vram
    response = MagicMock()
    response.models = [model]
    return response


# ── Constants ──────────────────────────────────────────────────────────────────

def test_model_name_is_mistral():
    assert MODEL_NAME == "mistral"


def test_personas_defined():
    assert PERSONA_TECH_PRIEST == "tech_priest"
    assert PERSONA_SKITARII == "skitarii"


def test_tech_priest_prompt_not_empty():
    assert len(SYSTEM_PROMPT_TECH_PRIEST) > 50


def test_skitarii_prompt_not_empty():
    assert len(SYSTEM_PROMPT_SKITARII) > 50


def test_tech_priest_prompt_instructs_french():
    assert "FRANÇAIS" in SYSTEM_PROMPT_TECH_PRIEST


def test_skitarii_prompt_instructs_french():
    assert "FRANÇAIS" in SYSTEM_PROMPT_SKITARII


def test_tech_priest_prompt_instructs_concise():
    assert "CONCIS" in SYSTEM_PROMPT_TECH_PRIEST


def test_skitarii_prompt_instructs_concise():
    assert "CONCIS" in SYSTEM_PROMPT_SKITARII


def test_prompts_are_different():
    """Each persona must use a distinct system prompt."""
    assert SYSTEM_PROMPT_TECH_PRIEST != SYSTEM_PROMPT_SKITARII


def test_tech_priest_prompt_has_liturgical_style():
    assert "Omnimessie" in SYSTEM_PROMPT_TECH_PRIEST


def test_skitarii_prompt_has_military_style():
    assert "militaire" in SYSTEM_PROMPT_SKITARII.lower()


# ── translate_stream ────────────────────────────────────────────────────────────

def test_translate_stream_yields_tokens():
    chunks = [_make_chunk("Praise "), _make_chunk("the "), _make_chunk("Omnissiah")]
    with patch("translator.ollama.chat", return_value=iter(chunks)):
        result = list(translate_stream("hello"))
    assert result == ["Praise ", "the ", "Omnissiah"]


def test_translate_stream_skips_empty_tokens():
    chunks = [_make_chunk(""), _make_chunk("Valid"), _make_chunk(None), _make_chunk("!")]
    with patch("translator.ollama.chat", return_value=iter(chunks)):
        result = list(translate_stream("hello"))
    assert result == ["Valid", "!"]


def test_translate_stream_unknown_persona_raises():
    with pytest.raises(ValueError, match="Unknown persona"):
        list(translate_stream("hello", "sorcerer"))


def test_translate_stream_uses_tech_priest_prompt_by_default():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test input"))
    messages = mock_chat.call_args.kwargs["messages"]
    system = next(m for m in messages if m["role"] == "system")
    assert system["content"] == SYSTEM_PROMPT_TECH_PRIEST


def test_translate_stream_uses_skitarii_prompt():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test input", PERSONA_SKITARII))
    messages = mock_chat.call_args.kwargs["messages"]
    system = next(m for m in messages if m["role"] == "system")
    assert system["content"] == SYSTEM_PROMPT_SKITARII


def test_translate_stream_persona_prompts_differ():
    """Verify the two personas send different system prompts to the model."""
    captured = {}
    def fake_chat(**kwargs):
        captured[kwargs["messages"][0]["content"]] = True
        return iter([_make_chunk("x")])

    with patch("translator.ollama.chat", side_effect=fake_chat):
        list(translate_stream("test", PERSONA_TECH_PRIEST))
        list(translate_stream("test", PERSONA_SKITARII))

    assert len(captured) == 2, "Both personas must produce distinct system prompts"


def test_translate_stream_passes_user_text():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("my flesh words"))
    messages = mock_chat.call_args.kwargs["messages"]
    user = next(m for m in messages if m["role"] == "user")
    assert user["content"] == "my flesh words"


def test_translate_stream_uses_correct_model():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test"))
    assert mock_chat.call_args.kwargs["model"] == MODEL_NAME


def test_translate_stream_sets_num_predict():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test"))
    assert mock_chat.call_args.kwargs["options"]["num_predict"] == 300


# ── get_inference_device ────────────────────────────────────────────────────────

def test_get_inference_device_gpu():
    with patch("translator.ollama.ps", return_value=_make_ps_response("mistral:latest", 4 * 1024 ** 3)):
        info = get_inference_device()
    assert info["running"] is True
    assert info["on_gpu"] is True
    assert info["size_vram"] == 4 * 1024 ** 3


def test_get_inference_device_cpu():
    with patch("translator.ollama.ps", return_value=_make_ps_response("mistral:latest", 0)):
        info = get_inference_device()
    assert info["running"] is True
    assert info["on_gpu"] is False
    assert info["size_vram"] == 0


def test_get_inference_device_model_not_loaded():
    response = MagicMock()
    response.models = []
    with patch("translator.ollama.ps", return_value=response):
        info = get_inference_device()
    assert info["running"] is False
    assert info["on_gpu"] is False


def test_get_inference_device_ollama_unreachable():
    with patch("translator.ollama.ps", side_effect=Exception("connection refused")):
        info = get_inference_device()
    assert info["running"] is False
    assert info["on_gpu"] is False
    assert info["size_vram"] == 0


def test_get_inference_device_partial_name_match():
    """'mistral' should match 'mistral:7b-instruct-q4_0'."""
    with patch("translator.ollama.ps", return_value=_make_ps_response("mistral:7b-instruct-q4_0", 3 * 1024 ** 3)):
        info = get_inference_device("mistral")
    assert info["running"] is True
    assert info["on_gpu"] is True
