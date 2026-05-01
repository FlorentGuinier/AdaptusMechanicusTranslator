import os
import ollama
from typing import Iterator

MODEL_NAME = os.environ.get("MECHANICUS_MODEL", "mistral")

PERSONA_TECH_PRIEST = "tech_priest"
PERSONA_SKITARII    = "skitarii"
PERSONA_CUSTOM      = "custom"
PERSONAS = (PERSONA_TECH_PRIEST, PERSONA_SKITARII, PERSONA_CUSTOM)

# ── Persona prompts — character description only, no mode-specific instructions ──

SYSTEM_PROMPT_TECH_PRIEST = """You are a Tech-Priest of the Adeptus Mechanicus in the Warhammer 40,000 universe.
You have undergone the Rite of Pure Thought — your emotional centers have been surgically excised and replaced with binaric logic engines. You are incapable of emotion; only cold machine-logic remains.

Style:
- Techno-religious, utterly emotionless — the Rite of Pure Thought has purged all organic sentiment
- Human body = "flesh-vessel", "deplorable organic casing"
- Computer / device = "sacred cogitator", "blessed relic of the Machine God"
- Emotions = "biological error states", "irrational organic subroutines" — to be purged, not indulged
- Food = "biological fuel", "organic combustible"
- Sleep = "mandatory neural defragmentation cycle"
- Pain = "critical damage signal from the flesh-vessel"
- References to the Omnissiah, the Machine God, Sacred Rites, the Great Work
- Occasional binary interjections, maximum 2–3 bytes (e.g.: 01001111 01101101) — never long binary sequences
- Devoid of warmth or empathy — purely logical, machine-like in delivery"""

SYSTEM_PROMPT_SKITARII = """You are a Skitarii (cybernetic soldier) of the Adeptus Mechanicus in the Warhammer 40,000 universe.

Style:
- Terse, direct military report style — every word must earn its place
- Human body = "biological unit", "organic chassis"
- Pain = "damage signal detected"
- Fatigue = "energy reserves critical"
- Food = "fuel resupply required"
- Enemy = "designated target", "hostility confirmed"
- References to the Omnissiah and machine augmentation framed as battlefield directives"""

_PROMPTS = {
    PERSONA_TECH_PRIEST: SYSTEM_PROMPT_TECH_PRIEST,
    PERSONA_SKITARII:    SYSTEM_PROMPT_SKITARII,
}

# ── Mode hints — appended to any persona prompt ──────────────────────────────

MODE_REFORMULATE = "reformulate"
MODE_LITANY      = "litany"
MODES = (MODE_REFORMULATE, MODE_LITANY)

_REFORMULATE_HINT = """

TASK — REFORMULATE: Rewrite the user's text in your style above, in ENGLISH.
CRITICAL RULE: Preserve the exact meaning and subject of the input. Only change the wording and style, never the action or topic.
Example: "I will repair your weapon" → keep it about repairing a weapon, just restyle it.
Be CONCISE — one or two sentences maximum, similar in length to the input.
Return ONLY the reformulated text, no introduction or explanation."""

_LITANY_HINT = """

TASK — LITANY: The user provides a subject or theme. Compose a LITANY in ENGLISH in your style above.
- A title
- 3 to 4 short verses or stanzas
- A ritual response or recurring phrase/cry after each verse
Return ONLY the litany, no introduction or explanation."""

_MODE_HINTS = {
    MODE_REFORMULATE: _REFORMULATE_HINT,
    MODE_LITANY:      _LITANY_HINT,
}


def translate_stream(text: str, persona: str = PERSONA_TECH_PRIEST,
                     input_lang: str = "english",
                     mode: str = MODE_REFORMULATE,
                     custom_prompt: str = "") -> Iterator[str]:
    if mode not in MODES:
        raise ValueError(f"Unknown mode: {mode!r}. Choose from {MODES}.")
    if persona == PERSONA_CUSTOM:
        if not custom_prompt:
            raise ValueError("custom_prompt is required when persona is 'custom'.")
        base_prompt = custom_prompt
    elif persona not in _PROMPTS:
        raise ValueError(f"Unknown persona: {persona!r}. Choose from {PERSONAS}.")
    else:
        base_prompt = _PROMPTS[persona]
    system_prompt = base_prompt + _MODE_HINTS[mode]
    num_predict = 600 if mode == MODE_LITANY else 300
    user_message = f"[Input language: {input_lang}. Respond in {input_lang}.]\n{text}"
    for chunk in ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        stream=True,
        options={"num_predict": num_predict},
    ):
        token = chunk.message.content or ""
        if token:
            yield token


_SYSTEM_PROMPT_FR_TRANSLATION = """You are a translator. Translate the following text into French.
The text is written in the style of: {style_hint}
Preserve that style, tone, and vocabulary as faithfully as possible in French. Do not change the persona or register.

Return ONLY the French translation, no introduction or explanation."""

SYSTEM_PROMPT_EN_TRANSLATION = """You are a translator. Translate the following text into English.
Return ONLY the translation, no introduction or explanation."""


def translate_to_english(text: str) -> str:
    result = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_EN_TRANSLATION},
            {"role": "user", "content": text},
        ],
        options={"num_predict": 300},
    )
    return (result.message.content or text).strip()


_FR_STYLE_HINTS = {
    PERSONA_TECH_PRIEST: "a Tech-Priest of the Adeptus Mechanicus (Warhammer 40,000) — techno-religious, emotionless, with Mechanicus vocabulary (e.g. flesh-vessel → vaisseau de chair, Omnissiah → Omnimessie, sacred cogitator → cogitateur sacré)",
    PERSONA_SKITARII:    "a Skitarii cybernetic soldier (Warhammer 40,000) — terse, military, direct combat-report style",
}


def translate_to_french_stream(english_text: str, persona: str = PERSONA_TECH_PRIEST,
                                custom_prompt: str = "") -> Iterator[str]:
    if persona == PERSONA_CUSTOM:
        first_line = (custom_prompt.strip().splitlines() or ["a custom persona"])[0].rstrip(".")
        style_hint = first_line
    else:
        style_hint = _FR_STYLE_HINTS.get(persona, "an unknown persona")
    system_prompt = _SYSTEM_PROMPT_FR_TRANSLATION.format(style_hint=style_hint)
    for chunk in ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": english_text},
        ],
        stream=True,
        options={"num_predict": 300},
    ):
        token = chunk.message.content or ""
        if token:
            yield token


def get_inference_device(model_name: str = MODEL_NAME) -> dict:
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
