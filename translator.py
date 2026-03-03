"""
translator.py — Core translation logic, no GUI dependency.
"""
import ollama
from typing import Iterator

MODEL_NAME = "mistral"

PERSONA_TECH_PRIEST = "tech_priest"
PERSONA_SKITARII    = "skitarii"
PERSONAS = (PERSONA_TECH_PRIEST, PERSONA_SKITARII)

SYSTEM_PROMPT_TECH_PRIEST = """Tu es un Prêtre-Technicien (Tech-Priest) de l'Adeptus Mechanicus dans l'univers Warhammer 40,000.
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
- Ton savant, quasi-liturgique, condescendant envers tout ce qui est "de la chair"

IMPORTANT : Sois CONCIS — une ou deux phrases maximum, similaire en longueur au texte d'entrée.
Retourne UNIQUEMENT la reformulation, sans introduction ni explication."""

SYSTEM_PROMPT_SKITARII = """Tu es un Skitarii (soldat cybernétique) de l'Adeptus Mechanicus dans l'univers Warhammer 40,000.
Reformule tout texte reçu dans le style martial et mécanique d'un Skitarii, en FRANÇAIS.

Règles de style obligatoires :
- Langage militaire, bref, direct, efficace — tu es un soldat, pas un théologien
- Corps humain = "unité biologique", "châssis organique"
- Douleur = "signal de dommage détecté"
- Fatigue = "réserves énergétiques critiques"
- Nourriture = "ravitaillement en carburant"
- Ennemi = "cible désignée", "hostilité confirmée"
- Références à la mission, au protocole, aux directives reçues
- Phrases courtes, style rapport militaire ou ordre de mission
- Pas de longs discours liturgiques — rester factuel et opérationnel

IMPORTANT : Sois CONCIS — une ou deux phrases maximum, similaire en longueur au texte d'entrée.
Retourne UNIQUEMENT la reformulation, sans introduction ni explication."""

_PROMPTS = {
    PERSONA_TECH_PRIEST: SYSTEM_PROMPT_TECH_PRIEST,
    PERSONA_SKITARII:    SYSTEM_PROMPT_SKITARII,
}


def translate_stream(text: str, persona: str = PERSONA_TECH_PRIEST) -> Iterator[str]:
    """
    Yield translation tokens one by one in Adeptus Mechanicus style.

    Args:
        text:    Input text to translate.
        persona: Speaking persona — PERSONA_TECH_PRIEST or PERSONA_SKITARII.

    Yields:
        Non-empty string tokens as they are generated.

    Raises:
        ValueError: If persona is unknown.
    """
    if persona not in _PROMPTS:
        raise ValueError(f"Unknown persona: {persona!r}. Choose from {PERSONAS}.")
    for chunk in ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": _PROMPTS[persona]},
            {"role": "user", "content": text},
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
