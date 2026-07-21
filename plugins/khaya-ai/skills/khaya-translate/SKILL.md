---
name: khaya-translate
description: Translate text between English and African languages (Twi, Ewe, Ga, Fante, Dagbani, Yoruba, Kikuyu, Gurene, Luo, Kimeru, Kusaal, and more) using the Khaya AI Translation v2 API. Use this skill whenever the user wants to translate to or from a Ghanaian or African language, localize content into African languages, mentions Khaya AI or GhanaNLP translation, or asks what a phrase means in Twi, Ewe, Ga, or another supported language. Requires a Khaya AI API key in the KHAYA_API_KEY environment variable.
---

# Khaya AI Machine Translation (v2)

Translates text between Ghanaian and African languages. Base URL: `https://translation-api.ghananlp.org/v2`

## Requirements

The only credential needed is a Khaya AI API key (an Azure APIM subscription key), read from the `KHAYA_API_KEY` environment variable. If it is not set, ask the user for their key and export it for the session (or pass `--api-key`). Users can get a key by subscribing at https://translation.ghananlp.org

Scripts use only the Python standard library - no packages to install.

## Workflow

```bash
# English to Twi
python scripts/translate.py "Hello, how are you?" --from eng --to twi

# Twi to English, reading from and writing to files
python scripts/translate.py --input letter.txt --from twi --to eng --output letter_en.txt

# Equivalent explicit pair form
python scripts/translate.py "Good morning" --lang eng-gaa

# List supported languages
python scripts/list_languages.py
```

The API accepts at most 1000 characters per request. The script handles longer text automatically by splitting on sentence boundaries, translating each chunk, and joining the results - no action needed, but for very long documents expect one API call per ~1000 characters.

## Language codes

`lang` is a hyphenated source-target pair of ISO 639-3 codes, e.g. `eng-twi`, `twi-eng`, `eng-yor`. Old two-letter codes (`en`, `tw`, `ee`, `yo`, `ki`) are rejected with a 400 naming the replacement.

Snapshot of supported codes (fetch the live list with `scripts/list_languages.py` or `GET /languages`): `eng` English, `twi` Twi, `ewe` Ewe, `gaa` Ga, `fat` Fante, `yor` Yoruba, `dag` Dagbani, `kik` Kikuyu, `gur` Gurene, `luo` Luo, `mer` Kimeru, `kus` Kusaal.

## API reference (for direct calls without the scripts)

Auth: header `Ocp-Apim-Subscription-Key: $KHAYA_API_KEY` (or query param `subscription-key`).

| Operation | Request |
|---|---|
| List languages | `GET /languages` returns `{"languages": {"eng": "English", "twi": "Twi", ...}}` (code to display name) |
| Translate | `POST /translate` with JSON body `{"in": "<text, max 1000 chars>", "lang": "eng-twi"}` |

The 200 response body is the translated text as a JSON string (e.g. `"Wo ho te sen?"`).

Errors come back as `{"error": {"code", "message", "details": [{"code", "target", "message"}]}}` - 400 `VALIDATION_FAILED` (detail codes: `UNSUPPORTED_LANGUAGE_CODE`, `UNSUPPORTED_LANGUAGE_PAIR`, `MISSING_TEXT`, `MISSING_LANGUAGE_PAIR`), 500 `SYSTEM_ERROR`. The scripts print these legibly; relay the message (it often names the fix, e.g. "Use 'eng' instead of 'en'") to the user.
