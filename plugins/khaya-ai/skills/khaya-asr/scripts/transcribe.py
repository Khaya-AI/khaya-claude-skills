#!/usr/bin/env python3
"""Transcribe an audio file with the Khaya AI ASR v3 API.

Examples:
    python transcribe.py recording.mp3 --language twi
    python transcribe.py talk.wav --language ewe --timestamps word --json -o out.json

Auth: set KHAYA_API_KEY (or pass --api-key). Get a key at https://translation.ghananlp.org
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.environ.get("KHAYA_ASR_BASE_URL", "https://translation-api.ghananlp.org/asr/v3")

CONTENT_TYPES = {
    ".mp3": "audio/mpeg",
    ".mpga": "audio/mpeg",
    ".mpeg": "audio/mpeg",
    ".wav": "audio/wav",
    ".wave": "audio/wav",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".opus": "audio/ogg",
}


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
    p = argparse.ArgumentParser(description="Transcribe audio via Khaya AI ASR v3.")
    p.add_argument("audio_file", help="Path to an MP3, WAV, FLAC, or OGG file")
    p.add_argument("--language", "-l", required=True,
                   help="ISO 639-3 code of the spoken language (e.g. twi, ewe, gaa). "
                        "Run list_languages.py for the full list.")
    p.add_argument("--timestamps", "-t", choices=["word", "segment"],
                   help="Include word- or segment-level timings in the response")
    p.add_argument("--json", action="store_true", dest="as_json",
                   help="Output the full JSON response instead of just the text")
    p.add_argument("--output", "-o", help="Write result to this file instead of stdout")
    p.add_argument("--api-key", help="Khaya AI API key (overrides KHAYA_API_KEY)")
    p.add_argument("--timeout", type=int, default=600,
                   help="Request timeout in seconds (default 600; long audio takes time)")
    args = p.parse_args()

    key = get_api_key(args.api_key)

    if not os.path.isfile(args.audio_file):
        sys.exit("Error: file not found: {}".format(args.audio_file))
    ext = os.path.splitext(args.audio_file)[1].lower()
    content_type = CONTENT_TYPES.get(ext)
    if not content_type:
        sys.exit("Error: unsupported audio extension '{}'. Supported: MP3, WAV, FLAC, OGG. "
                 "Convert first, e.g.: ffmpeg -i input{} output.wav".format(ext, ext))

    with open(args.audio_file, "rb") as f:
        audio = f.read()
    if not audio:
        sys.exit("Error: {} is empty.".format(args.audio_file))

    params = {"language": args.language}
    if args.timestamps:
        params["timestamps"] = args.timestamps
    url = "{}/transcribe?{}".format(BASE_URL, urllib.parse.urlencode(params))

    req = urllib.request.Request(
        url,
        data=audio,
        method="POST",
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": content_type,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        sys.exit(format_api_error(e.code, e.read().decode("utf-8", "replace")))
    except urllib.error.URLError as e:
        sys.exit("Network error reaching {}: {}".format(BASE_URL, e.reason))

    result = json.loads(body)
    out = json.dumps(result, ensure_ascii=False, indent=2) if args.as_json else result.get("text", "")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print("Saved transcription to {}".format(args.output))
    else:
        print(out)


if __name__ == "__main__":
    main()
