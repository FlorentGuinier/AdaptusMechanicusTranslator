import os
import re
import shutil
import subprocess
import threading
import time
import webbrowser

import questionary
from questionary import Choice

_MODELS = [
    ("mistral:7b",    "~4 GB",  "recommended · good balance"),
    ("llama3.2:3b",   "~2 GB",  "fast · lightweight"),
    ("llama3.1:8b",   "~5 GB",  "better quality"),
    ("gemma3:4b",     "~3 GB",  "fast · efficient"),
    ("qwen2.5:7b",    "~4 GB",  "multilingual"),
    ("phi4:14b",      "~9 GB",  "high quality · slower"),
    ("llama3.3:70b",  "~40 GB", "best quality · very slow"),
]
_DEFAULT = "mistral:7b"


def _pick_model() -> str:
    choices = [
        Choice(
            title=f"{name:<20} [{vram:<8} VRAM]  {note}",
            value=name,
        )
        for name, vram, note in _MODELS
    ]
    return questionary.select(
        "Select model:",
        choices=choices,
        default=_DEFAULT,
    ).ask() or _DEFAULT


def _ensure_model(model_name: str) -> None:
    try:
        import ollama
        available = {getattr(m, "model", getattr(m, "name", "")) for m in ollama.list().models}
        if model_name in available:
            return
        print(f"Pulling {model_name} — this may take a few minutes...")
        for progress in ollama.pull(model_name, stream=True):
            status = getattr(progress, "status", "") or ""
            completed = getattr(progress, "completed", None)
            total = getattr(progress, "total", None)
            if total:
                pct = int(completed / total * 100) if completed else 0
                print(f"\r  {status} {pct}%   ", end="", flush=True)
            elif status:
                print(f"\r  {status}   ", end="", flush=True)
        print(f"\r  Done.{' ' * 50}")
    except Exception as e:
        print(f"Warning: could not pull {model_name}: {e}")


if __name__ == "__main__":
    model = _pick_model()
    print()
    _ensure_model(model)

    os.environ["MECHANICUS_MODEL"] = model
    print(f"Using model: {model}\n")

    from server import app

    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False), daemon=True).start()
    time.sleep(0.8)

    webbrowser.open("http://localhost:5000")

    cloudflared = shutil.which("cloudflared")
    if cloudflared:
        proc = subprocess.Popen(
            [cloudflared, "tunnel", "--url", "http://localhost:5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        url_shown = False
        for line in proc.stdout:
            if not url_shown:
                m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if m:
                    url = m.group(0)
                    print("\n" + "━" * 56)
                    print(f"  URL A PARTAGER :  {url}")
                    print("━" * 56 + "\n")
                    url_shown = True

        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            print("\nShutdown.")
    else:
        print("(cloudflared not found — sharing disabled. Install: winget install Cloudflare.cloudflared)")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print("\nShutdown.")
