"""
Unit tests for translator.py — no GUI, no live Ollama connection required.
"""
import pytest
from unittest.mock import MagicMock, patch

import translator
from translator import (
    translate_stream, translate_to_english, translate_to_french_stream,
    get_inference_device, MODEL_NAME, PERSONA_TECH_PRIEST, PERSONA_SKITARII,
    PERSONAS, SYSTEM_PROMPT_TECH_PRIEST, SYSTEM_PROMPT_SKITARII,
    SYSTEM_PROMPT_FR_TRANSLATION, SYSTEM_PROMPT_EN_TRANSLATION,
    MODE_REFORMULATE, MODE_LITANY, MODES,
    SYSTEM_PROMPT_LITANY_TECH_PRIEST, SYSTEM_PROMPT_LITANY_SKITARII,
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


def test_personas_tuple_contains_both():
    assert PERSONA_TECH_PRIEST in PERSONAS
    assert PERSONA_SKITARII in PERSONAS


def test_tech_priest_prompt_not_empty():
    assert len(SYSTEM_PROMPT_TECH_PRIEST) > 50


def test_skitarii_prompt_not_empty():
    assert len(SYSTEM_PROMPT_SKITARII) > 50


def test_tech_priest_prompt_instructs_english():
    assert "ENGLISH" in SYSTEM_PROMPT_TECH_PRIEST


def test_skitarii_prompt_instructs_english():
    assert "ENGLISH" in SYSTEM_PROMPT_SKITARII


def test_tech_priest_prompt_instructs_concise():
    assert "CONCISE" in SYSTEM_PROMPT_TECH_PRIEST


def test_skitarii_prompt_instructs_concise():
    assert "MAXIMUM" in SYSTEM_PROMPT_SKITARII


def test_prompts_are_different():
    """Each persona must use a distinct system prompt."""
    assert SYSTEM_PROMPT_TECH_PRIEST != SYSTEM_PROMPT_SKITARII


def test_tech_priest_prompt_has_liturgical_style():
    assert "Omnissiah" in SYSTEM_PROMPT_TECH_PRIEST


def test_skitarii_prompt_has_military_style():
    assert "military" in SYSTEM_PROMPT_SKITARII.lower()


def test_tech_priest_prompt_rite_of_pure_thought():
    """Tech-Priest must have undergone the Rite of Pure Thought — no emotions."""
    assert "Rite of Pure Thought" in SYSTEM_PROMPT_TECH_PRIEST


def test_tech_priest_prompt_emotionless():
    """Tech-Priest prompt must explicitly describe emotionless state."""
    assert "emotion" in SYSTEM_PROMPT_TECH_PRIEST.lower()


# ── Modes ──────────────────────────────────────────────────────────────────────

def test_modes_defined():
    assert MODE_REFORMULATE == "reformulate"
    assert MODE_LITANY == "litany"


def test_modes_tuple_contains_both():
    assert MODE_REFORMULATE in MODES
    assert MODE_LITANY in MODES


# ── Litany prompts ─────────────────────────────────────────────────────────────

def test_litany_tech_priest_prompt_not_empty():
    assert len(SYSTEM_PROMPT_LITANY_TECH_PRIEST) > 50


def test_litany_skitarii_prompt_not_empty():
    assert len(SYSTEM_PROMPT_LITANY_SKITARII) > 50


def test_litany_prompts_are_different():
    assert SYSTEM_PROMPT_LITANY_TECH_PRIEST != SYSTEM_PROMPT_LITANY_SKITARII


def test_litany_prompts_differ_from_reformulation_prompts():
    assert SYSTEM_PROMPT_LITANY_TECH_PRIEST != SYSTEM_PROMPT_TECH_PRIEST
    assert SYSTEM_PROMPT_LITANY_SKITARII != SYSTEM_PROMPT_SKITARII


def test_litany_tech_priest_prompt_instructs_english():
    assert "ENGLISH" in SYSTEM_PROMPT_LITANY_TECH_PRIEST


def test_litany_skitarii_prompt_instructs_english():
    assert "ENGLISH" in SYSTEM_PROMPT_LITANY_SKITARII


def test_litany_tech_priest_prompt_mentions_litany():
    assert "litany" in SYSTEM_PROMPT_LITANY_TECH_PRIEST.lower()


def test_litany_skitarii_prompt_mentions_litany():
    assert "litany" in SYSTEM_PROMPT_LITANY_SKITARII.lower()


def test_litany_tech_priest_has_verses():
    """Tech-Priest litany should describe a verse/title structure."""
    assert "title" in SYSTEM_PROMPT_LITANY_TECH_PRIEST.lower()


def test_litany_skitarii_has_title():
    """Skitarii battle litany should describe a title."""
    assert "title" in SYSTEM_PROMPT_LITANY_SKITARII.lower()


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


def test_translate_stream_unknown_mode_raises():
    with pytest.raises(ValueError, match="Unknown mode"):
        list(translate_stream("hello", mode="chant"))


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
    assert "my flesh words" in user["content"]


def test_translate_stream_includes_input_lang_hint():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", input_lang="french"))
    messages = mock_chat.call_args.kwargs["messages"]
    user = next(m for m in messages if m["role"] == "user")
    assert "french" in user["content"].lower()


def test_translate_stream_uses_correct_model():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test"))
    assert mock_chat.call_args.kwargs["model"] == MODEL_NAME


def test_translate_stream_reformulate_sets_num_predict_300():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", mode=MODE_REFORMULATE))
    assert mock_chat.call_args.kwargs["options"]["num_predict"] == 300


def test_translate_stream_litany_sets_num_predict_600():
    """Litany mode needs more tokens for a structured multi-verse output."""
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("cogitator", mode=MODE_LITANY))
    assert mock_chat.call_args.kwargs["options"]["num_predict"] == 600


def test_translate_stream_litany_uses_litany_tech_priest_prompt():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", PERSONA_TECH_PRIEST, mode=MODE_LITANY))
    messages = mock_chat.call_args.kwargs["messages"]
    system = next(m for m in messages if m["role"] == "system")
    assert system["content"] == SYSTEM_PROMPT_LITANY_TECH_PRIEST


def test_translate_stream_litany_uses_litany_skitarii_prompt():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", PERSONA_SKITARII, mode=MODE_LITANY))
    messages = mock_chat.call_args.kwargs["messages"]
    system = next(m for m in messages if m["role"] == "system")
    assert system["content"] == SYSTEM_PROMPT_LITANY_SKITARII


def test_translate_stream_litany_prompts_differ_per_persona():
    """Litany mode must also produce distinct prompts for each persona."""
    captured = {}
    def fake_chat(**kwargs):
        captured[kwargs["messages"][0]["content"]] = True
        return iter([_make_chunk("x")])

    with patch("translator.ollama.chat", side_effect=fake_chat):
        list(translate_stream("test", PERSONA_TECH_PRIEST, mode=MODE_LITANY))
        list(translate_stream("test", PERSONA_SKITARII, mode=MODE_LITANY))

    assert len(captured) == 2, "Both personas must produce distinct litany prompts"


def test_translate_stream_reformulate_does_not_use_litany_prompt():
    """Reformulate mode must NOT use litany prompts."""
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", PERSONA_TECH_PRIEST, mode=MODE_REFORMULATE))
    messages = mock_chat.call_args.kwargs["messages"]
    system = next(m for m in messages if m["role"] == "system")
    assert system["content"] != SYSTEM_PROMPT_LITANY_TECH_PRIEST


# ── translate_to_english ───────────────────────────────────────────────────────

def test_translate_to_english_returns_string():
    mock_result = MagicMock()
    mock_result.message.content = "The flesh-vessel hungers"
    with patch("translator.ollama.chat", return_value=mock_result):
        result = translate_to_english("Le vaisseau de chair a faim")
    assert result == "The flesh-vessel hungers"


def test_translate_to_english_uses_en_translation_prompt():
    mock_result = MagicMock()
    mock_result.message.content = "ok"
    with patch("translator.ollama.chat", return_value=mock_result) as mock_chat:
        translate_to_english("Bonjour")
    messages = mock_chat.call_args.kwargs["messages"]
    system = next(m for m in messages if m["role"] == "system")
    assert system["content"] == SYSTEM_PROMPT_EN_TRANSLATION


def test_translate_to_english_passes_text():
    mock_result = MagicMock()
    mock_result.message.content = "hello"
    with patch("translator.ollama.chat", return_value=mock_result) as mock_chat:
        translate_to_english("bonjour")
    messages = mock_chat.call_args.kwargs["messages"]
    user = next(m for m in messages if m["role"] == "user")
    assert user["content"] == "bonjour"


def test_translate_to_english_falls_back_on_empty_response():
    mock_result = MagicMock()
    mock_result.message.content = ""
    with patch("translator.ollama.chat", return_value=mock_result):
        result = translate_to_english("bonjour")
    assert result == "bonjour"  # returns original text as fallback


def test_translate_to_english_strips_whitespace():
    mock_result = MagicMock()
    mock_result.message.content = "  hello world  "
    with patch("translator.ollama.chat", return_value=mock_result):
        result = translate_to_english("bonjour")
    assert result == "hello world"


# ── translate_to_french_stream ─────────────────────────────────────────────────

def test_translate_to_french_stream_yields_tokens():
    chunks = [_make_chunk("Le vaisseau"), _make_chunk(" de chair")]
    with patch("translator.ollama.chat", return_value=iter(chunks)):
        result = list(translate_to_french_stream("The flesh-vessel"))
    assert result == ["Le vaisseau", " de chair"]


def test_translate_to_french_stream_uses_fr_translation_prompt():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_to_french_stream("The flesh-vessel hungers"))
    messages = mock_chat.call_args.kwargs["messages"]
    system = next(m for m in messages if m["role"] == "system")
    assert system["content"] == SYSTEM_PROMPT_FR_TRANSLATION


def test_translate_to_french_stream_prompt_differs_from_main_prompts():
    assert SYSTEM_PROMPT_FR_TRANSLATION != SYSTEM_PROMPT_TECH_PRIEST
    assert SYSTEM_PROMPT_FR_TRANSLATION != SYSTEM_PROMPT_SKITARII


def test_translate_to_french_stream_passes_english_text():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_to_french_stream("sacred cogitator activated"))
    messages = mock_chat.call_args.kwargs["messages"]
    user = next(m for m in messages if m["role"] == "user")
    assert user["content"] == "sacred cogitator activated"


def test_translate_to_french_stream_skips_empty_tokens():
    chunks = [_make_chunk(""), _make_chunk("Le "), _make_chunk(None), _make_chunk("vaisseau")]
    with patch("translator.ollama.chat", return_value=iter(chunks)):
        result = list(translate_to_french_stream("The flesh-vessel"))
    assert result == ["Le ", "vaisseau"]


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


def test_get_inference_device_returns_dict_keys():
    """Response must always contain all three expected keys."""
    with patch("translator.ollama.ps", side_effect=Exception("down")):
        info = get_inference_device()
    assert set(info.keys()) == {"running", "on_gpu", "size_vram"}


def test_get_inference_device_size_vram_is_int():
    with patch("translator.ollama.ps", return_value=_make_ps_response("mistral", 2 * 1024 ** 3)):
        info = get_inference_device()
    assert isinstance(info["size_vram"], int)
