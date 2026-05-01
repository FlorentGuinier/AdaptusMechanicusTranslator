import os
import threading
import webbrowser


def _pick_model() -> str:
    try:
        import ollama
        models = [getattr(m, "model", getattr(m, "name", "")) for m in ollama.list().models if getattr(m, "model", getattr(m, "name", ""))]
    except Exception:
        return "mistral"

    if not models:
        return "mistral"

    default = next((m for m in models if "mistral" in m.lower()), models[0])

    print("\nAvailable models:")
    for i, name in enumerate(models, 1):
        marker = " (default)" if name == default else ""
        print(f"  {i}. {name}{marker}")

    try:
        choice = input(f"\nSelect model [Enter = {default}]: ").strip()
        if choice:
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]
    except (ValueError, KeyboardInterrupt):
        pass

    return default


if __name__ == "__main__":
    model = _pick_model()
    os.environ["MECHANICUS_MODEL"] = model
    print(f"\nUsing model: {model}\n")

    from server import app

    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
