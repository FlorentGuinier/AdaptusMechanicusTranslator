#!/usr/bin/env python3
"""
cli.py — Quick translation test without the GUI.

Usage:
    uv run python cli.py "your text here"
    uv run python cli.py "your text here" --persona skitarii
    uv run python cli.py "cogitator" --mode litany
    echo "your text" | uv run python cli.py
"""
import argparse
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from translator import (translate_stream, PERSONA_TECH_PRIEST, PERSONA_SKITARII,
                        MODE_REFORMULATE, MODE_LITANY)


def main() -> None:
    parser = argparse.ArgumentParser(description="Adeptus Mechanicus translator CLI")
    parser.add_argument("text", nargs="?", help="Text to translate (reads stdin if omitted)")
    parser.add_argument("--persona", choices=[PERSONA_TECH_PRIEST, PERSONA_SKITARII],
                        default=PERSONA_TECH_PRIEST,
                        help="Speaking persona (default: tech_priest)")
    parser.add_argument("--mode", choices=[MODE_REFORMULATE, MODE_LITANY],
                        default=MODE_REFORMULATE,
                        help="Output mode: reformulate a phrase or compose a litany (default: reformulate)")
    args = parser.parse_args()

    text = args.text or sys.stdin.read().strip()
    if not text:
        parser.error("No text provided.")

    print(f"[{args.persona.upper()}] [{args.mode.upper()}] {text}\n")

    try:
        for token in translate_stream(text, args.persona, mode=args.mode):
            print(token, end="", flush=True)
        print()
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
