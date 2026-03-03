#!/usr/bin/env python3
"""
cli.py — Quick translation test without the GUI.

Usage:
    uv run python cli.py "your text here"
    uv run python cli.py "your text here" --lang fr
    uv run python cli.py "your text here" --lang en
    uv run python cli.py "your text here" --lang both   (default)
    echo "your text" | uv run python cli.py
"""
import argparse
import sys
from translator import translate_stream


def stream_translation(text: str, language: str, header: str) -> None:
    print(f"\n── {header} {'─' * (52 - len(header))}")
    for token in translate_stream(text, language):
        print(token, end="", flush=True)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Adeptus Mechanicus translator CLI")
    parser.add_argument("text", nargs="?", help="Text to translate (reads stdin if omitted)")
    parser.add_argument("--lang", choices=["fr", "en", "both"], default="both",
                        help="Output language (default: both)")
    args = parser.parse_args()

    text = args.text or sys.stdin.read().strip()
    if not text:
        parser.error("No text provided.")

    print(f"INPUT: {text}")

    try:
        if args.lang in ("fr", "both"):
            stream_translation(text, "fr", "LINGUA FRANCIUM")
        if args.lang in ("en", "both"):
            stream_translation(text, "en", "LINGUA IMPERIALIS")
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
