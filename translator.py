"""
translator.py — Core translation logic, no GUI dependency.
"""
import ollama
from typing import Iterator

MODEL_NAME = "mistral"

SYSTEM_PROMPT = """Tu es un Prêtre-Technicien (Tech-Priest) de l'Adeptus Mechanicus dans l'univers Warhammer 40,000.
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
- Ton légèrement condescendant envers tout ce qui est "de la chair"

IMPORTANT : Sois CONCIS — une ou deux phrases maximum, similaire en longueur au texte d'entrée.
Retourne UNIQUEMENT la reformulation, sans introduction ni explication."""


def translate_stream(text: str) -> Iterator[str]:
    """
    Yield translation tokens one by one in Adeptus Mechanicus style.
    Responds in the same language as the input text.

    Args:
        text: Input text to translate.

    Yields:
        Non-empty string tokens as they are generated.
    """
    for chunk in ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
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
