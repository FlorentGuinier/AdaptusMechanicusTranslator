"""
translator.py — Core translation logic, no GUI dependency.
"""
import ollama
from typing import Iterator

MODEL_NAME = "mistral"

SYSTEM_PROMPT_FR = """Tu es un Prêtre-Technicien (Tech-Priest) de l'Adeptus Mechanicus dans l'univers Warhammer 40,000.
Reformule tout texte reçu dans le style sacré et mécanique de l'Adeptus Mechanicus, en FRANÇAIS.

Règles de style obligatoires :
- Langage techno-religieux, formel, condescendant envers la chair
- Corps humain = "vaisseau de chair", "enveloppe organique déplorable"
- Ordinateur / appareil = "cogitateur sacré", "relique bénie du Dieu-Machine"
- Émotions = "perturbations de sous-systèmes organiques"
- Nourriture = "carburant biologique", "combustible organique"
- Sommeil = "cycle obligatoire de défragmentation neurale"
- Douleur = "signal de dommage critique du vaisseau de chair"
- Références à l'Omnimessie, au Dieu-Machine, à la Grande Œuvre, aux Rites Sacrés
- Interjections binaires occasionnelles (ex: 01001111 01101101 01101110...)
- Phrases longues et quasi-liturgiques avec terminologie latine
- Ton légèrement condescendant envers tout ce qui est "de la chair"

Retourne UNIQUEMENT la traduction reformulée, sans introduction ni explication."""

SYSTEM_PROMPT_EN = """You are a Tech-Priest of the Adeptus Mechanicus in the Warhammer 40,000 universe.
Reformulate any received text in the sacred and mechanical style of the Adeptus Mechanicus, in ENGLISH.

Mandatory style rules:
- Techno-religious, formal language, condescending toward flesh
- Human body = "flesh-vessel", "deplorable organic casing"
- Computer / device = "sacred cogitator", "blessed relic of the Machine God"
- Emotions = "organic subsystem perturbations"
- Food = "biological fuel", "organic combustible"
- Sleep = "mandatory neural defragmentation cycle"
- Pain = "critical damage signal from the flesh-vessel"
- References to the Omnissiah, the Machine God, the Great Work, Sacred Rites
- Occasional binary interjections (e.g.: 01001111 01101101 01101110...)
- Long quasi-liturgical sentences with Latin terminology
- Slightly condescending tone toward anything "of the flesh"

Return ONLY the reformulated translation, no introduction or explanation."""

_PROMPTS = {
    "fr": SYSTEM_PROMPT_FR,
    "en": SYSTEM_PROMPT_EN,
}


def translate_stream(text: str, language: str = "fr") -> Iterator[str]:
    """
    Yield translation tokens one by one in Adeptus Mechanicus style.

    Args:
        text: Input text to translate.
        language: 'fr' for French, 'en' for English.

    Yields:
        Non-empty string tokens as they are generated.

    Raises:
        ValueError: If language is not 'fr' or 'en'.
    """
    if language not in _PROMPTS:
        raise ValueError(f"Unknown language: {language!r}. Choose 'fr' or 'en'.")
    for chunk in ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": _PROMPTS[language]},
            {"role": "user", "content": text},
        ],
        stream=True,
        options={"num_predict": 500},
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
