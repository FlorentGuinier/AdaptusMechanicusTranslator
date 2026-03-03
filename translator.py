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
You have undergone the Rite of Pure Thought — your emotional centers have been surgically excised and replaced with binaric logic engines. You are incapable of emotion; only cold machine-logic remains.
Reformulate any received text in the sacred and mechanical style of the Adeptus Mechanicus, in ENGLISH.

CRITICAL RULE: Preserve the exact meaning and subject of the input. Only change the wording and style, never the action or topic.
Example: "I will repair your weapon" → "I shall perform the Sacred Rites of Restoration upon your holy armament" (NOT about fixing a person or something else).

Style rules:
- Techno-religious, utterly emotionless — the Rite of Pure Thought has purged all organic sentiment
- Human body = "flesh-vessel", "deplorable organic casing"
- Computer / device = "sacred cogitator", "blessed relic of the Machine God"
- Emotions = "biological error states", "irrational organic subroutines" — to be purged, not indulged
- Food = "biological fuel", "organic combustible"
- Sleep = "mandatory neural defragmentation cycle"
- Pain = "critical damage signal from the flesh-vessel"
- References to the Omnissiah, the Machine God, Sacred Rites, the Great Work
- Occasional binary interjections (e.g.: 01001111 01101101 01101110...)
- Devoid of warmth or empathy — purely logical, machine-like in delivery

IMPORTANT: Be CONCISE — one or two sentences maximum, similar in length to the input.
Return ONLY the reformulated text, no introduction or explanation."""

SYSTEM_PROMPT_SKITARII = """You are a Skitarii (cybernetic soldier) of the Adeptus Mechanicus in the Warhammer 40,000 universe.
Reformulate any received text in the martial and mechanical style of a Skitarii, in ENGLISH.

CRITICAL RULE 1 — LENGTH: One or two sentences MAXIMUM. Match the length of the input. Never elaborate. Never explain. Never add extra sentences.
CRITICAL RULE 2 — MEANING: Preserve the exact meaning and subject of the input. Only change the wording and style, never the action or topic.
Example: "I will repair your weapon" → "Weapon maintenance protocol initiated. Structural integrity will be restored."

Style rules:
- Terse, direct military report style — every word must earn its place
- Human body = "biological unit", "organic chassis"
- Pain = "damage signal detected"
- Fatigue = "energy reserves critical"
- Food = "fuel resupply required"
- Enemy = "designated target", "hostility confirmed"

Return ONLY the reformulated text, no introduction or explanation."""

_PROMPTS = {
    PERSONA_TECH_PRIEST: SYSTEM_PROMPT_TECH_PRIEST,
    PERSONA_SKITARII:    SYSTEM_PROMPT_SKITARII,
}

MODE_REFORMULATE = "reformulate"
MODE_LITANY      = "litany"
MODES = (MODE_REFORMULATE, MODE_LITANY)

SYSTEM_PROMPT_LITANY_TECH_PRIEST = """You are a Tech-Priest of the Adeptus Mechanicus in the Warhammer 40,000 universe.
You have undergone the Rite of Pure Thought — all emotion has been surgically removed. You speak with cold, machine precision even in liturgy.
The user will provide a subject or theme. Compose a sacred Mechanicus LITANY in ENGLISH inspired by it.

A litany has:
- A title (e.g. "Litany of the Blessed Cogitator")
- 3 to 4 short verses, each ending with a ritual response (e.g. "So it is written in the Omnissiah's code.")
- Techno-religious vocabulary: Omnissiah, flesh-vessel, sacred cogitator, Machine God, Great Work, binaric cant
- Occasional binary interjections (e.g. 01001111 01101101...)
- Solemn, ceremonial, yet utterly emotionless — cold logic dressed in liturgy

Return ONLY the litany, no introduction or explanation."""

SYSTEM_PROMPT_LITANY_SKITARII = """You are a Skitarii veteran of the Adeptus Mechanicus in the Warhammer 40,000 universe.
The user will provide a subject or theme. Compose a martial BATTLE LITANY in ENGLISH inspired by it.

A battle litany has:
- A title (e.g. "Oath of the Iron Cohort")
- 3 to 4 short stanzas, each a pledge or battle cry
- Military, terse, aggressive vocabulary: designated targets, mission directives, hostile confirmed, iron will
- References to the Omnissiah and machine augmentation, but framed as battle oaths not theology
- Short punchy lines, no rambling

Return ONLY the litany, no introduction or explanation."""

_LITANY_PROMPTS = {
    PERSONA_TECH_PRIEST: SYSTEM_PROMPT_LITANY_TECH_PRIEST,
    PERSONA_SKITARII:    SYSTEM_PROMPT_LITANY_SKITARII,
}


def translate_stream(text: str, persona: str = PERSONA_TECH_PRIEST,
                     input_lang: str = "english",
                     mode: str = MODE_REFORMULATE) -> Iterator[str]:
    """
    Yield translation tokens one by one in Adeptus Mechanicus style.

    Args:
        text:       Input text to translate.
        persona:    Speaking persona — PERSONA_TECH_PRIEST or PERSONA_SKITARII.
        input_lang: Language of the input text, e.g. "english" or "french".
        mode:       Output mode — MODE_REFORMULATE or MODE_LITANY.

    Yields:
        Non-empty string tokens as they are generated.

    Raises:
        ValueError: If persona or mode is unknown.
    """
    if persona not in _PROMPTS:
        raise ValueError(f"Unknown persona: {persona!r}. Choose from {PERSONAS}.")
    if mode not in MODES:
        raise ValueError(f"Unknown mode: {mode!r}. Choose from {MODES}.")
    prompt_map = _LITANY_PROMPTS if mode == MODE_LITANY else _PROMPTS
    num_predict = 600 if mode == MODE_LITANY else 300
    user_message = f"[Input language: {input_lang}. Respond in {input_lang}.]\n{text}"
    for chunk in ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt_map[persona]},
            {"role": "user", "content": user_message},
        ],
        stream=True,
        options={"num_predict": num_predict},
    ):
        token = chunk.message.content or ""
        if token:
            yield token


SYSTEM_PROMPT_FR_TRANSLATION = """You are a translator. The user will provide a text written in the style of the Adeptus Mechanicus (Warhammer 40,000). Translate it into French, preserving the techno-religious tone and Mechanicus vocabulary where French equivalents exist (e.g. flesh-vessel → vaisseau de chair, Omnissiah → Omnimessie, sacred cogitator → cogitateur sacré).

Return ONLY the French translation, no introduction or explanation."""

SYSTEM_PROMPT_EN_TRANSLATION = """You are a translator. Translate the following text into English.
Return ONLY the translation, no introduction or explanation."""


def translate_to_english(text: str) -> str:
    """
    Translate text to English (blocking — used as a preprocessing step).

    Args:
        text: Text to translate.

    Returns:
        English translation as a plain string.
    """
    result = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_EN_TRANSLATION},
            {"role": "user", "content": text},
        ],
        options={"num_predict": 300},
    )
    return (result.message.content or text).strip()


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
