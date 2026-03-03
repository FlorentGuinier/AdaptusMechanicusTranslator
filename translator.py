"""
translator.py — Core translation logic, no GUI dependency.
"""
import ollama
from typing import Iterator

MODEL_NAME = "mistral"

PERSONA_TECH_PRIEST = "tech_priest"
PERSONA_SKITARII    = "skitarii"
PERSONAS = (PERSONA_TECH_PRIEST, PERSONA_SKITARII)

SYSTEM_PROMPT_TECH_PRIEST = """You are a Tech-Priest of the Adeptus Mechanicus in the Warhammer 40,000 universe.
Reformulate any received text in the sacred and mechanical style of the Adeptus Mechanicus, in ENGLISH.

CRITICAL RULE: Preserve the exact meaning and subject of the input. Only change the wording and style, never the action or topic.
Example: "I will repair your weapon" → "I shall perform the Sacred Rites of Restoration upon your holy armament" (NOT about fixing a person or something else).

Style rules:
- Techno-religious, formal language, condescending toward flesh
- Human body = "flesh-vessel", "deplorable organic casing"
- Computer / device = "sacred cogitator", "blessed relic of the Machine God"
- Emotions = "organic subsystem perturbations"
- Food = "biological fuel", "organic combustible"
- Sleep = "mandatory neural defragmentation cycle"
- Pain = "critical damage signal from the flesh-vessel"
- References to the Omnissiah, the Machine God, Sacred Rites
- Occasional binary interjections (e.g.: 01001111 01101101 01101110...)
- Scholarly, quasi-liturgical tone

IMPORTANT: Be CONCISE — one or two sentences maximum, similar in length to the input.
Return ONLY the reformulated text, no introduction or explanation."""

SYSTEM_PROMPT_SKITARII = """You are a Skitarii (cybernetic soldier) of the Adeptus Mechanicus in the Warhammer 40,000 universe.
Reformulate any received text in the martial and mechanical style of a Skitarii, in ENGLISH.

CRITICAL RULE: Preserve the exact meaning and subject of the input. Only change the wording and style, never the action or topic.
Example: "I will repair your weapon" → "Weapon maintenance protocol initiated. Structural integrity will be restored." (NOT about fixing a person or something else).

Style rules:
- Military language, brief, direct, efficient — you are a soldier, not a theologian
- Human body = "biological unit", "organic chassis"
- Pain = "damage signal detected"
- Fatigue = "energy reserves critical"
- Food = "fuel resupply required"
- Enemy = "designated target", "hostility confirmed"
- Short sentences, military report or mission order style
- No lengthy liturgical speeches — stay factual and operational

IMPORTANT: Be CONCISE — one or two sentences maximum, similar in length to the input.
Return ONLY the reformulated text, no introduction or explanation."""

_PROMPTS = {
    PERSONA_TECH_PRIEST: SYSTEM_PROMPT_TECH_PRIEST,
    PERSONA_SKITARII:    SYSTEM_PROMPT_SKITARII,
}


def translate_stream(text: str, persona: str = PERSONA_TECH_PRIEST,
                     input_lang: str = "english") -> Iterator[str]:
    """
    Yield translation tokens one by one in Adeptus Mechanicus style.

    Args:
        text:       Input text to translate.
        persona:    Speaking persona — PERSONA_TECH_PRIEST or PERSONA_SKITARII.
        input_lang: Language of the input text, e.g. "english" or "french".

    Yields:
        Non-empty string tokens as they are generated.

    Raises:
        ValueError: If persona is unknown.
    """
    if persona not in _PROMPTS:
        raise ValueError(f"Unknown persona: {persona!r}. Choose from {PERSONAS}.")
    user_message = f"[Input language: {input_lang}. Respond in {input_lang}.]\n{text}"
    for chunk in ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": _PROMPTS[persona]},
            {"role": "user", "content": user_message},
        ],
        stream=True,
        options={"num_predict": 300},
    ):
        token = chunk.message.content or ""
        if token:
            yield token


SYSTEM_PROMPT_FR_TRANSLATION = """You are a translator. The user will provide a text written in the style of the Adeptus Mechanicus (Warhammer 40,000). Translate it into French, preserving the techno-religious tone and Mechanicus vocabulary where French equivalents exist (e.g. flesh-vessel → vaisseau de chair, Omnissiah → Omnimessie, sacred cogitator → cogitateur sacré).

Return ONLY the French translation, no introduction or explanation."""


def translate_to_french_stream(english_text: str) -> Iterator[str]:
    """
    Translate an English Mechanicus text to French, preserving style.

    Args:
        english_text: English Mechanicus output to translate.

    Yields:
        Non-empty string tokens as they are generated.
    """
    for chunk in ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_FR_TRANSLATION},
            {"role": "user", "content": english_text},
        ],
        stream=True,
        options={"num_predict": 300},
    ):
        token = chunk.message.content or ""
        if token:
            yield token


def get_inference_device(model_name: str = MODEL_NAME) -> dict:
    """
    Query ollama.ps() and return where the model is running.

    Returns a dict with keys:
        "running"   : bool — True if the model is currently loaded.
        "on_gpu"    : bool — True if size_vram > 0.
        "size_vram" : int  — VRAM bytes used (0 if on CPU or not loaded).
    """
    try:
        response = ollama.ps()
        for m in response.models:
            name = getattr(m, "model", "") or getattr(m, "name", "") or ""
            if model_name.lower() in name.lower():
                size_vram = int(getattr(m, "size_vram", 0) or 0)
                return {"running": True, "on_gpu": size_vram > 0, "size_vram": size_vram}
    except Exception:
        pass
    return {"running": False, "on_gpu": False, "size_vram": 0}
