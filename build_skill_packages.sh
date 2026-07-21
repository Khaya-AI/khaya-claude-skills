#!/usr/bin/env bash
# Build uploadable .skill packages (zip archives) from the skill directories.
set -euo pipefail
cd "$(dirname "$0")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p dist
for skill in plugins/khaya-ai/skills/*/; do
  name=$(basename "$skill")
  (cd "plugins/khaya-ai/skills" && zip -qr "$TMP/$name.skill" "$name" -x "*/__pycache__/*")
  cp "$TMP/$name.skill" "dist/$name.skill"
  echo "built dist/$name.skill"
done
