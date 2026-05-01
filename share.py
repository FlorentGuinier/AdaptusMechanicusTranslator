import os
import re
import shutil
import subprocess
import sys
import threading
import time

import questionary


def _pick_model() -> str:
    try:
        import ollama
        models = [getattr(m, "model", getattr(m, "name", "")) for m in ollama.list().models if getattr(m, "model", getattr(m, "name", ""))]
    except Exception:
        return "mistral"

    if not models:
        return "mistral"

    default = next((m for m in models if "mistral" in m.lower()), models[0])

    return questionary.select(
        "Select model:",
        choices=models,
        default=default,
    ).ask() or default


def main():
    cloudflared = shutil.which("cloudflared")
    if not cloudflared:
        sys.exit("cloudflared not found. Install it: winget install Cloudflare.cloudflared")

    model = _pick_model()
    os.environ["MECHANICUS_MODEL"] = model
    print(f"\nUsing model: {model}\n")

    from server import app

    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False), daemon=True).start()
    time.sleep(0.8)

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


if __name__ == "__main__":
    main()
