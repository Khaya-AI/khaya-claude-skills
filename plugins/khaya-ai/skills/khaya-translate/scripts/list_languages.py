#!/usr/bin/env python3
"""List the languages supported by the Khaya AI Translation v2 API.

Auth: set KHAYA_API_KEY (or pass --api-key).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ.get("KHAYA_MT_BASE_URL", "https://translation-api.ghananlp.org/v2")


def main():
    p = argparse.ArgumentParser(description="List Khaya AI Translation v2 supported languages.")
    p.add_argument("--json", action="store_true", dest="as_json", help="Output raw JSON")
    p.add_argument("--api-key", help="Khaya AI API key (overrides KHAYA_API_KEY)")
    args = p.parse_args()

    key = args.api_key or os.environ.get("KHAYA_API_KEY")
    if not key:
        sys.exit("Error: no API key found. Set KHAYA_API_KEY or pass --api-key. "
                 "Subscribe at https://translation.ghananlp.org to get one.")

    req = urllib.request.Request(
        BASE_URL + "/languages",
        headers={"Ocp-Apim-Subscription-Key": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            sys.exit("API error {}: authentication failed. Check that KHAYA_API_KEY is a valid, "
                     "active Khaya AI subscription key.".format(e.code))
        sys.exit("API error {}: {}".format(e.code, e.read().decode("utf-8", "replace")[:500]))
    except urllib.error.URLError as e:
        sys.exit("Network error reaching {}: {}".format(BASE_URL, e.reason))

    data = json.loads(body)
    if args.as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    langs = data.get("languages", {})
    for code in sorted(langs, key=lambda c: langs[c]):
        print("{}  {}".format(code.ljust(4), langs[code]))
    print("\n{} languages. Use pairs like eng-twi or twi-eng in --lang.".format(len(langs)))


if __name__ == "__main__":
    main()
