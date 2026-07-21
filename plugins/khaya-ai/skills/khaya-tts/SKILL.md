---
name: khaya-tts
description: Convert text into natural-sounding speech audio in 32 African languages and dialects (Asante Twi, Akuapem Twi, Fante, Ewe, Ga, Dagbani, Hausa, Igbo, Swahili, Yoruba, Wolof, Krio, Pidgin, and more) using the Khaya AI Text-to-Speech v2 API. Use this skill whenever the user wants text read aloud, spoken audio, voiceovers, audio versions of text, or TTS in a Ghanaian or African language, mentions Khaya AI or GhanaNLP speech synthesis, or asks to generate WAV/MP3/OGG speech from text. Requires a Khaya AI API key in the KHAYA_API_KEY environment variable.
---

# Khaya AI Text-to-Speech (TTS v2)

Synthesizes text into audio across 32 languages and dialects, with three voices. Base URL: `https://translation-api.ghananlp.org/tts/v2`

## Requirements

The only credential needed is a Khaya AI API key (an Azure APIM subscription key), read from the `KHAYA_API_KEY` environment variable. If it is not set, ask the user for their key and export it for the session (or pass `--api-key`). Users can get a key by subscribing at https://translation.ghananlp.org

Scripts use only the Python standard library - no packages to install.

## Workflow

```bash
# Synthesize Twi speech to WAV (default voice for the language)
python scripts/synthesize.py "Wo ho te sen?" --language twi --output greeting.wav

# Choose a voice and MP3 output
python scripts/synthesize.py "Mia woezor" --language ewe --speaker female --format mp3 -o welcome.mp3

# Read the text from a file
python scripts/synthesize.py --text-file story.txt --language dag -o story.wav

# Discover languages and voices
python scripts/list_voices.py
```

Voices (`--speaker`): `male_low`, `male_high`, `female`. The same three voices work for every language; omit to use the language's default. Output formats: `wav` (default), `mp3`, `ogg`.

## Language codes

Codes are ISO 639-3. Old two-letter codes (`tw`, `ee`, ...) are rejected with a 400 naming the replacement. Note that some dialects have their own codes and voice models - they are not aliases: Asante Twi `twi` vs Akuapem Twi `atw`; Konkomba Likpakpaanl `xon` vs Likoonli `lxn`.

| Language | Code | Language | Code | Language | Code | Language | Code |
|---|---|---|---|---|---|---|---|
| Akuapem Twi | atw | Fante | fat | Kikuyu | kik | Nzema | nzi |
| Asante Twi | twi | French | fra | Konkomba (Likpakpaanl) | xon | Pidgin | pcm |
| Dagaare | dga | Ga | gaa | Konkomba (Likoonli) | lxn | Shona | sna |
| Dagbani | dag | Gonja | gjn | Krio | kri | Swahili | swa |
| Dangme | ada | Gurene | gur | Kusaal | kus | Temne | tem |
| English | eng | Hausa | hau | Luo | luo | Wali | wlx |
| Ewe | ewe | Igbo | ibo | Mampruli | maw | Wolof | wol |
| | | Kasem | xsm | Mende | men | Yoruba | yor |
| | | | | Meru/Kimeru | mer | | |

Fetch the live list with `python scripts/list_voices.py` (or `GET /languages`) if in doubt.

## API reference (for direct calls without the scripts)

Auth: header `Ocp-Apim-Subscription-Key: $KHAYA_API_KEY` (or query param `subscription-key`).

| Operation | Request |
|---|---|
| List languages | `GET /languages` returns `{"languages": {"Asante Twi": "twi", ...}}` (display name to code) |
| List speakers | `GET /speakers` returns `{"speakers": {"Multilingual": ["male_low", "male_high", "female"]}}` |
| Synthesize | `POST /synthesize` with JSON body below; response body is the audio bytes, `Content-Type: audio/wav|mp3|ogg` |

```json
{
  "text": "Wo ho te sen?",      // required
  "language": "twi",            // required, ISO 639-3
  "speaker_id": "male_low",     // optional; default voice per language
  "stream": false,              // optional; true streams wav/mp3 as generated
  "format": "wav"               // optional: wav (default), mp3, ogg
}
```

Errors come back as `{"error": {"code", "message", "details": [{"code", "target", "message"}]}}` - 400 `VALIDATION_FAILED` (detail codes: `EMPTY_TEXT`, `MISSING_LANGUAGE`, `UNSUPPORTED_LANGUAGE`, `INVALID_SPEAKER`, `INVALID_REQUEST`), 500 `SYSTEM_ERROR`. The scripts print these legibly; relay the message (it often names the fix) to the user.
