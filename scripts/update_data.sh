#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/data"

curl -sL "https://raw.githubusercontent.com/ThePandemoniumInstitute/botc-translations/main/game/de.json" \
  -o "$DATA/de-official.json"
curl -sL "https://raw.githubusercontent.com/RealVidy/botc-translations/main/assets/json/en_GB.json" \
  -o "$DATA/characters-en.json"
curl -sL "https://raw.githubusercontent.com/RealVidy/botc-translations/main/assets/json/de_DE.json" \
  -o "$DATA/characters-de-community.json"

echo "Updated data snapshots in $DATA"
