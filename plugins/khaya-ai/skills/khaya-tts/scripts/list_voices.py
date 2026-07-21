#!/usr/bin/env python3
"""List the languages and speaker voices supported by the Khaya AI TTS v2 API.

Auth: set KHAYA_API_KEY (or pass --api-key).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ.get("KHAYA_TTS_BASE_URL", "https://translation-api.ghananlp.org/tts/v2")


def fetch(path, key):
    req = urllib.request.Request(BASE_URL + path, headers={"Ocp-Apim-Subscription-Key": key})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            sys.exit("API error {}: authentication failed. Check that KHAYA_API_KEY is a valid, "
                     "active Khaya AI subscription key.".format(e.code))
        sys.exit("API error {} on {}: {}".format(e.code, path, e.read().decode("utf-8", "replace")[:500]))
    except urllib.error.URLError as e:
        sys.exit("Network error reaching {}: {}".format(BASE_URL, e.reason))


def main():
    p = argparse.ArgumentParser(description="List Khaya AI TTS v2 languages and voices.")
    p.add_argument("--json", action="store_true", dest="as_json", help="Output raw JSON")
    p.add_argument("--api-key", help="Khaya AI API key (overrides KHAYA_API_KEY)")
    args = p.parse_args()

    key = args.api_key or os.environ.get("KHAYA_API_KEY")
    if not key:
        sys.exit("Error: no API key found. Set KHAYA_API_KEY or pass --api-key. "
                 "Subscribe at https://translation.ghananlp.org to get one.")

    languages = fetch("/languages", key).get("languages", {})
    speakers = fetch("/speakers", key).get("speakers", {})

    if args.as_json:
        print(json.dumps({"languages": languages, "speakers": speakers}, ensure_ascii=False, indent=2))
        return

    print("Languages ({}):".format(len(languages)))
    width = max((len(name) for name in languages), default=8)
    for name in sorted(languages):
        print("  {}  {}".format(name.ljust(width), languages[name]))
    print("\nSpeakers (usable with every language):")
    for group, ids in speakers.items():
        print("  {}: {}".format(group, ", ".join(ids)))


if __name__ == "__main__":
    main()
