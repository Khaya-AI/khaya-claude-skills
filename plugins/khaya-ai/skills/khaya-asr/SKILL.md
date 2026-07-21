---
name: khaya-asr
description: Transcribe speech to text in 34 African languages (Twi, Ewe, Ga, Dagbani, Fante, Hausa, Swahili, Yoruba, and more) using the Khaya AI ASR v3 API. Use this skill whenever the user wants to transcribe, caption, subtitle, or convert audio or voice recordings in a Ghanaian or African language into text, asks for speech recognition / speech-to-text / ASR for African languages, mentions Khaya AI or GhanaNLP transcription, or needs word- or segment-level timestamps for African-language audio. Requires a Khaya AI API key in the KHAYA_API_KEY environment variable.
---

# Khaya AI Automatic Speech Recognition (ASR v3)

Transcribes audio to text in 34 Ghanaian and African languages. Supports long-form audio and optional word- or segment-level timing. Base URL: `https://translation-api.ghananlp.org/asr/v3`

## Requirements

The only credential needed is a Khaya AI API key (an Azure APIM subscription key), read from the `KHAYA_API_KEY` environment variable. If it is not set, ask the user for their key and export it for the session (or pass `--api-key`). Users can get a key by subscribing at https://translation.ghananlp.org

Scripts use only the Python standard library - no packages to install.

## Workflow

1. If the language of the audio is unknown or its code is uncertain, list supported languages first:

   ```bash
   python scripts/list_languages.py
   ```

   Language codes are ISO 639-3 (three letters, e.g. `twi`, `ewe`, `gaa`). Two-letter codes like `tw` or `ee` are rejected by the API with a message naming the correct code.

2. Transcribe:

   ```bash
   # Plain transcription (prints the text)
   python scripts/transcribe.py recording.mp3 --language twi

   # With word-level timestamps, saved as JSON
   python scripts/transcribe.py recording.wav --language ewe --timestamps word --json --output transcript.json

   # Segment-level timestamps (good for subtitles)
   python scripts/transcribe.py interview.flac --language dag --timestamps segment --json
   ```

Accepted audio formats: MP3, WAV, FLAC, OGG. If the user's file is in another format (m4a, video, etc.), convert it first with ffmpeg (`ffmpeg -i in.m4a out.wav`) before transcribing. Timestamp support can vary by language - if the API returns `UNSUPPORTED_TIMESTAMPS`, retry without `--timestamps` and tell the user.

For subtitle output (.srt/.vtt), request `--timestamps segment --json` and convert the `timings.segments` array (each entry has `text`, `start`, `end` in seconds).

## API reference (for direct calls without the scripts)

Auth: header `Ocp-Apim-Subscription-Key: $KHAYA_API_KEY` (or query param `subscription-key`).

| Operation | Request |
|---|---|
| List languages | `GET /languages` returns `{"languages": [{"code": "ewe", "name": "Ewe"}, ...]}` |
| Transcribe | `POST /transcribe?language=<code>[&timestamps=word\|segment]` - body is the raw audio bytes; `Content-Type` must match the audio (`audio/mpeg`, `audio/wav`, `audio/flac`, or `audio/ogg`) |

Successful response:

```json
{
  "text": "full transcribed text",
  "timings": {
    "unit": "seconds",
    "granularity": "word",
    "words":    [{"word": "Hello", "start": 0.0, "end": 0.4}],
    "segments": [{"text": "Hello world", "start": 0.0, "end": 0.9}]
  }
}
```

`timings` is present only when `timestamps=` was set; `words` is populated for `timestamps=word`, `segments` for `timestamps=segment`.

Errors come back as `{"error": {"code", "message", "details": [{"code", "target", "message"}]}}` - 400 `VALIDATION_FAILED` (detail codes: `EMPTY_AUDIO`, `UNSUPPORTED_LANGUAGE`, `INVALID_AUDIO_FORMAT`, `INVALID_TIMESTAMPS`, `UNSUPPORTED_TIMESTAMPS`), 500 `SYSTEM_ERROR`. The scripts already print these legibly; relay the message (which often names the fix, e.g. "Use 'twi' instead") to the user.
