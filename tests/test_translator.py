"""
Unit tests for translator.py — no GUI, no live Ollama connection required.
"""
import pytest
from unittest.mock import MagicMock, patch

import translator
from translator import translate_stream, get_inference_device, MODEL_NAME


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


def test_prompt_not_empty():
    assert len(translator.SYSTEM_PROMPT) > 50


def test_prompt_instructs_french():
    assert "FRANÇAIS" in translator.SYSTEM_PROMPT


def test_prompt_instructs_concise():
    assert "CONCIS" in translator.SYSTEM_PROMPT


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


def test_translate_stream_uses_system_prompt():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test input"))
    messages = mock_chat.call_args.kwargs["messages"]
    system = next(m for m in messages if m["role"] == "system")
    assert system["content"] == translator.SYSTEM_PROMPT


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
