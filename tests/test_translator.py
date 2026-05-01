import pytest
from unittest.mock import MagicMock, patch

import translator
from translator import (
    translate_stream, translate_to_english, translate_to_french_stream,
    get_inference_device, MODEL_NAME, PERSONA_TECH_PRIEST, PERSONA_SKITARII,
    PERSONA_CUSTOM, PERSONAS, SYSTEM_PROMPT_TECH_PRIEST, SYSTEM_PROMPT_SKITARII,
    SYSTEM_PROMPT_EN_TRANSLATION,
    MODE_REFORMULATE, MODE_LITANY, MODES,
    _REFORMULATE_HINT, _LITANY_HINT,
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
    assert PERSONA_CUSTOM == "custom"


def test_personas_tuple_contains_all():
    assert PERSONA_TECH_PRIEST in PERSONAS
    assert PERSONA_SKITARII in PERSONAS
    assert PERSONA_CUSTOM in PERSONAS


def test_tech_priest_prompt_not_empty():
    assert len(SYSTEM_PROMPT_TECH_PRIEST) > 50


def test_skitarii_prompt_not_empty():
    assert len(SYSTEM_PROMPT_SKITARII) > 50


def test_tech_priest_prompt_rite_of_pure_thought():
    assert "Rite of Pure Thought" in SYSTEM_PROMPT_TECH_PRIEST


def test_tech_priest_prompt_emotionless():
    assert "emotion" in SYSTEM_PROMPT_TECH_PRIEST.lower()


def test_tech_priest_prompt_has_liturgical_style():
    assert "Omnissiah" in SYSTEM_PROMPT_TECH_PRIEST


def test_skitarii_prompt_has_military_style():
    assert "military" in SYSTEM_PROMPT_SKITARII.lower()


def test_prompts_are_different():
    assert SYSTEM_PROMPT_TECH_PRIEST != SYSTEM_PROMPT_SKITARII


# ── Modes ──────────────────────────────────────────────────────────────────────

def test_modes_defined():
    assert MODE_REFORMULATE == "reformulate"
    assert MODE_LITANY == "litany"


def test_modes_tuple_contains_both():
    assert MODE_REFORMULATE in MODES
    assert MODE_LITANY in MODES


def test_reformulate_hint_not_empty():
    assert len(_REFORMULATE_HINT) > 20


def test_litany_hint_not_empty():
    assert len(_LITANY_HINT) > 20


def test_hints_are_different():
    assert _REFORMULATE_HINT != _LITANY_HINT


def test_litany_hint_mentions_litany():
    assert "litany" in _LITANY_HINT.lower() or "LITANY" in _LITANY_HINT


def test_reformulate_hint_mentions_concise():
    assert "CONCISE" in _REFORMULATE_HINT or "concise" in _REFORMULATE_HINT.lower()


# ── translate_stream ───────────────────────────────────────────────────────────

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
    assert SYSTEM_PROMPT_TECH_PRIEST in system["content"]


def test_translate_stream_uses_skitarii_prompt():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test input", PERSONA_SKITARII))
    messages = mock_chat.call_args.kwargs["messages"]
    system = next(m for m in messages if m["role"] == "system")
    assert SYSTEM_PROMPT_SKITARII in system["content"]


def test_translate_stream_persona_prompts_differ():
    captured = {}
    def fake_chat(**kwargs):
        captured[kwargs["messages"][0]["content"]] = True
        return iter([_make_chunk("x")])
    with patch("translator.ollama.chat", side_effect=fake_chat):
        list(translate_stream("test", PERSONA_TECH_PRIEST))
        list(translate_stream("test", PERSONA_SKITARII))
    assert len(captured) == 2


def test_translate_stream_reformulate_appends_reformulate_hint():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", mode=MODE_REFORMULATE))
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert _REFORMULATE_HINT in system["content"]


def test_translate_stream_litany_appends_litany_hint():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", mode=MODE_LITANY))
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert _LITANY_HINT in system["content"]


def test_translate_stream_reformulate_does_not_include_litany_hint():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", mode=MODE_REFORMULATE))
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert _LITANY_HINT not in system["content"]


def test_translate_stream_litany_persona_prompts_still_differ():
    captured = {}
    def fake_chat(**kwargs):
        captured[kwargs["messages"][0]["content"]] = True
        return iter([_make_chunk("x")])
    with patch("translator.ollama.chat", side_effect=fake_chat):
        list(translate_stream("test", PERSONA_TECH_PRIEST, mode=MODE_LITANY))
        list(translate_stream("test", PERSONA_SKITARII, mode=MODE_LITANY))
    assert len(captured) == 2


def test_translate_stream_custom_persona_uses_custom_prompt():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", PERSONA_CUSTOM, custom_prompt="Be a pirate."))
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert "Be a pirate." in system["content"]


def test_translate_stream_custom_persona_empty_prompt_raises():
    with pytest.raises(ValueError, match="custom_prompt"):
        list(translate_stream("hello", PERSONA_CUSTOM, custom_prompt=""))


def test_translate_stream_custom_persona_no_prompt_raises():
    with pytest.raises(ValueError, match="custom_prompt"):
        list(translate_stream("hello", PERSONA_CUSTOM))


def test_translate_stream_custom_litany_includes_litany_hint():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", PERSONA_CUSTOM, custom_prompt="Be an Ork.", mode=MODE_LITANY))
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert _LITANY_HINT in system["content"]
    assert "Be an Ork." in system["content"]


def test_translate_stream_passes_user_text():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("my flesh words"))
    user = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "user")
    assert "my flesh words" in user["content"]


def test_translate_stream_includes_input_lang_hint():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("test", input_lang="french"))
    user = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "user")
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
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_stream("cogitator", mode=MODE_LITANY))
    assert mock_chat.call_args.kwargs["options"]["num_predict"] == 600


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
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert system["content"] == SYSTEM_PROMPT_EN_TRANSLATION


def test_translate_to_english_passes_text():
    mock_result = MagicMock()
    mock_result.message.content = "hello"
    with patch("translator.ollama.chat", return_value=mock_result) as mock_chat:
        translate_to_english("bonjour")
    user = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "user")
    assert user["content"] == "bonjour"


def test_translate_to_english_falls_back_on_empty_response():
    mock_result = MagicMock()
    mock_result.message.content = ""
    with patch("translator.ollama.chat", return_value=mock_result):
        result = translate_to_english("bonjour")
    assert result == "bonjour"


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
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert "French" in system["content"] or "french" in system["content"]


def test_translate_to_french_stream_includes_persona_style_hint():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_to_french_stream("text", PERSONA_TECH_PRIEST))
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert "Tech-Priest" in system["content"]


def test_translate_to_french_stream_skitarii_hint():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_to_french_stream("text", PERSONA_SKITARII))
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert "Skitarii" in system["content"]


def test_translate_to_french_stream_custom_uses_first_line_of_prompt():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_to_french_stream("text", PERSONA_CUSTOM, custom_prompt="You are an Ork Warboss.\nMore stuff."))
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert "You are an Ork Warboss" in system["content"]


def test_translate_to_french_stream_prompt_differs_from_main_prompts():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_to_french_stream("text", PERSONA_TECH_PRIEST))
    system = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "system")
    assert system["content"] != SYSTEM_PROMPT_TECH_PRIEST
    assert system["content"] != SYSTEM_PROMPT_SKITARII


def test_translate_to_french_stream_passes_english_text():
    with patch("translator.ollama.chat", return_value=iter([_make_chunk("x")])) as mock_chat:
        list(translate_to_french_stream("sacred cogitator activated"))
    user = next(m for m in mock_chat.call_args.kwargs["messages"] if m["role"] == "user")
    assert user["content"] == "sacred cogitator activated"


def test_translate_to_french_stream_skips_empty_tokens():
    chunks = [_make_chunk(""), _make_chunk("Le "), _make_chunk(None), _make_chunk("vaisseau")]
    with patch("translator.ollama.chat", return_value=iter(chunks)):
        result = list(translate_to_french_stream("The flesh-vessel"))
    assert result == ["Le ", "vaisseau"]


# ── get_inference_device ───────────────────────────────────────────────────────

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
    with patch("translator.ollama.ps", return_value=_make_ps_response("mistral:7b-instruct-q4_0", 3 * 1024 ** 3)):
        info = get_inference_device("mistral")
    assert info["running"] is True
    assert info["on_gpu"] is True


def test_get_inference_device_returns_dict_keys():
    with patch("translator.ollama.ps", side_effect=Exception("down")):
        info = get_inference_device()
    assert set(info.keys()) == {"running", "on_gpu", "size_vram"}


def test_get_inference_device_size_vram_is_int():
    with patch("translator.ollama.ps", return_value=_make_ps_response("mistral", 2 * 1024 ** 3)):
        info = get_inference_device()
    assert isinstance(info["size_vram"], int)
