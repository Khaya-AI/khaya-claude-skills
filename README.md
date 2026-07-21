# Khaya AI Skills for Claude

[Claude](https://claude.ai) skills for the [Khaya AI](https://khaya.ai) APIs — speech and text AI for African languages:

| Skill | API | What it does |
|---|---|---|
| `khaya-asr` | ASR v3 | Transcribe audio to text in 34 African languages, with optional word/segment timestamps |
| `khaya-tts` | TTS v2 | Synthesize natural speech (WAV/MP3/OGG) in 32 languages and dialects, 3 voices |
| `khaya-translate` | Translation v2 | Translate between English and African languages (Twi, Ewe, Ga, Fante, Dagbani, Yoruba, and more) |

The only requirement is a Khaya AI API key — subscribe at [translation.ghananlp.org](https://translation.ghananlp.org), then set it as the `KHAYA_API_KEY` environment variable. The bundled scripts use only the Python standard library.

## Install

### Claude Code, Claude Desktop, or Cowork (recommended)

```
/plugin marketplace add Khaya-AI/khaya-claude-skills
/plugin install khaya-ai@khaya-ai
```

All three skills install together and trigger automatically when you ask Claude to transcribe, voice, or translate African-language content.

### Manual (per-skill)

Copy any skill directory from `plugins/khaya-ai/skills/` into `~/.claude/skills/`:

```bash
cp -r plugins/khaya-ai/skills/khaya-translate ~/.claude/skills/
```

### claude.ai / desktop app upload

Zip a skill directory with a `.skill` extension and upload it under **Settings → Capabilities**:

```bash
./build_skill_packages.sh   # writes khaya-asr.skill, khaya-tts.skill, khaya-translate.skill to dist/
```

(Team/Enterprise org owners can provision skills org-wide from admin settings.)

## Usage examples

Once installed, just ask Claude naturally:

- "Transcribe this Twi voice note and give me word-level timestamps"
- "Read this paragraph aloud in Ewe with the female voice, save as MP3"
- "Translate this letter from English to Dagbani"

Claude fetches supported languages live from the APIs (`GET /languages`), so new languages work without updating the skills.

## API documentation

Full API reference: [translation.ghananlp.org](https://translation.ghananlp.org) · Questions: subscriptions@khaya.ai

## License

MIT — see [LICENSE](LICENSE).
