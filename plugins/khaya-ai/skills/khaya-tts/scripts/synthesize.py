#!/usr/bin/env python3
"""Synthesize speech with the Khaya AI TTS v2 API.

Examples:
    python synthesize.py "Wo ho te sen?" --language twi -o greeting.wav
    python synthesize.py --text-file story.txt --language ewe --speaker female --format mp3 -o story.mp3

Auth: set KHAYA_API_KEY (or pass --api-key). Get a key at https://translation.ghananlp.org
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ.get("KHAYA_TTS_BASE_URL", "https://translation-api.ghananlp.org/tts/v2")


def get_api_key(cli_key):
    key = cli_key or os.environ.get("KHAYA_API_KEY")
    if not key:
        sys.exit(
            "Error: no API key found. Set the KHAYA_API_KEY environment variable "
            "or pass --api-key. Subscribe at https://translation.ghananlp.org to get one."
        )
    return key


def format_api_error(status, body):
    try:
        err = json.loads(body)["error"]
        lines = ["API error {} - {}: {}".format(status, err.get("code"), err.get("message"))]
        for d in err.get("details", []) or []:
            target = " [{}]".format(d.get("target")) if d.get("target") else ""
            lines.append("  - {}{}: {}".format(d.get("code"), target, d.get("message")))
        return "\n".join(lines)
    except (ValueError, KeyError, TypeError):
        if status in (401, 403):
            return ("API error {}: authentication failed. Check that KHAYA_API_KEY is a valid, "
                    "active Khaya AI subscription key.".format(status))
        return "API error {}: {}".format(status, body[:500])


def main():
    p = argparse.ArgumentParser(description="Synthesize speech via Khaya AI TTS v2.")
    p.add_argument("text", nargs="?", help="Text to synthesize (or use --text-file)")
    p.add_argument("--text-file", help="Read the text to synthesize from this file")
    p.add_argument("--language", "-l", required=True,
                   help="ISO 639-3 code (e.g. twi, atw, ewe, gaa). Run list_voices.py for the full list.")
    p.add_argument("--speaker", "-s", choices=["male_low", "male_high", "female"],
                   help="Voice to use; omit for the language's default voice")
    p.add_argument("--format", "-f", choices=["wav", "mp3", "ogg"], default="wav",
                   help="Audio output format (default wav)")
    p.add_argument("--output", "-o", help="Output file path (default: speech.<format>)")
    p.add_argument("--api-key", help="Khaya AI API key (overrides KHAYA_API_KEY)")
    p.add_argument("--timeout", type=int, default=600, help="Request timeout in seconds (default 600)")
    args = p.parse_args()

    key = get_api_key(args.api_key)

    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    elif args.text is not None:
        text = args.text.strip()
    else:
        p.error("provide TEXT as an argument or use --text-file")
    if not text:
        sys.exit("Error: the input text is empty.")

    payload = {"text": text, "language": args.language, "format": args.format}
    if args.speaker:
        payload["speaker_id"] = args.speaker

    req = urllib.request.Request(
        BASE_URL + "/synthesize",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            audio = resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(format_api_error(e.code, e.read().decode("utf-8", "replace")))
    except urllib.error.URLError as e:
        sys.exit("Network error reaching {}: {}".format(BASE_URL, e.reason))

    out_path = args.output or "speech.{}".format(args.format)
    with open(out_path, "wb") as f:
        f.write(audio)
    print("Saved {} bytes of {} audio to {}".format(len(audio), args.format, out_path))


if __name__ == "__main__":
    main()
