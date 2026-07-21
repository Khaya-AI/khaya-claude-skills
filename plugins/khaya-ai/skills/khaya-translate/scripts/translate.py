#!/usr/bin/env python3
"""Translate text with the Khaya AI Translation v2 API.

Examples:
    python translate.py "Hello, how are you?" --from eng --to twi
    python translate.py --input letter.txt --from twi --to eng --output letter_en.txt
    python translate.py "Good morning" --lang eng-gaa

Text longer than 1000 characters is split on sentence boundaries and translated
in chunks automatically (the API limit is 1000 characters per request).

Auth: set KHAYA_API_KEY (or pass --api-key). Get a key at https://translation.ghananlp.org
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ.get("KHAYA_MT_BASE_URL", "https://translation-api.ghananlp.org/v2")
MAX_CHARS = 1000


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


def chunk_text(text, limit=MAX_CHARS):
    """Split text into chunks of at most `limit` chars, preferring sentence
    boundaries, then word boundaries, then hard cuts."""
    if len(text) <= limit:
        return [text]
    sentences = re.split(r"(?<=[.!?…])\s+|\n+", text)
    chunks, current = [], ""
    for sentence in sentences:
        if not sentence:
            continue
        while len(sentence) > limit:  # single sentence longer than the limit
            cut = sentence.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            piece, sentence = sentence[:cut], sentence[cut:].lstrip()
            if current:
                chunks.append(current)
                current = ""
            chunks.append(piece)
        candidate = (current + " " + sentence).strip() if current else sentence
        if len(candidate) <= limit:
            current = candidate
        else:
            chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def translate_chunk(text, lang, key, timeout):
    req = urllib.request.Request(
        BASE_URL + "/translate",
        data=json.dumps({"in": text, "lang": lang}).encode("utf-8"),
        method="POST",
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        sys.exit(format_api_error(e.code, e.read().decode("utf-8", "replace")))
    except urllib.error.URLError as e:
        sys.exit("Network error reaching {}: {}".format(BASE_URL, e.reason))
    result = json.loads(body)  # response is the translated text as a JSON string
    if not isinstance(result, str):
        sys.exit("Unexpected response shape: {}".format(body[:500]))
    return result


def main():
    p = argparse.ArgumentParser(description="Translate text via Khaya AI Translation v2.")
    p.add_argument("text", nargs="?", help="Text to translate (or use --input)")
    p.add_argument("--input", "-i", help="Read the text to translate from this file")
    p.add_argument("--from", dest="src", metavar="CODE",
                   help="Source language ISO 639-3 code (e.g. eng)")
    p.add_argument("--to", dest="tgt", metavar="CODE",
                   help="Target language ISO 639-3 code (e.g. twi)")
    p.add_argument("--lang", help="Explicit source-target pair, e.g. eng-twi (alternative to --from/--to)")
    p.add_argument("--output", "-o", help="Write the translation to this file instead of stdout")
    p.add_argument("--api-key", help="Khaya AI API key (overrides KHAYA_API_KEY)")
    p.add_argument("--timeout", type=int, default=120, help="Per-request timeout in seconds (default 120)")
    args = p.parse_args()

    key = get_api_key(args.api_key)

    if args.lang:
        lang = args.lang
    elif args.src and args.tgt:
        lang = "{}-{}".format(args.src, args.tgt)
    else:
        p.error("specify --from and --to (or --lang eng-twi)")

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read().strip()
    elif args.text is not None:
        text = args.text.strip()
    else:
        p.error("provide TEXT as an argument or use --input")
    if not text:
        sys.exit("Error: the input text is empty.")

    chunks = chunk_text(text)
    if len(chunks) > 1:
        print("Input is {} characters; translating in {} chunks...".format(len(text), len(chunks)),
              file=sys.stderr)
    translated = " ".join(translate_chunk(c, lang, key, args.timeout) for c in chunks)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(translated)
        print("Saved translation to {}".format(args.output))
    else:
        print(translated)


if __name__ == "__main__":
    main()
