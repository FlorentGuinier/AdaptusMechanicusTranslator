import re
import subprocess
import sys
import threading
import time

from server import app


def _run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


def main():
    threading.Thread(target=_run_flask, daemon=True).start()
    time.sleep(0.8)

    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
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
