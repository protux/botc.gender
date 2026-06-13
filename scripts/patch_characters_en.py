#!/usr/bin/env python3
"""Fill missing editions and community image URLs in characters-en.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OFFICIAL_BASE = "https://release.botc.app/resources/characters"
TOWNSQUARE_IMAGE = (
    "https://github.com/bra1n/townsquare/blob/main/src/assets/icons/{role_id}.png?raw=true"
)

# Townsquare icons that are known to work when no official edition is available.
TOWNSQUARE_ONLY = {
    "stormcatcher",
}


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def community_image_url(role_id: str, team: str, edition: str | None) -> str:
    if edition == "fabled":
        return f"{OFFICIAL_BASE}/fabled/{role_id}.webp"

    if edition:
        suffix = "_e.webp" if team in {"minion", "demon"} else "_g.webp"
        return f"{OFFICIAL_BASE}/{edition}/{role_id}{suffix}"

    if role_id in TOWNSQUARE_ONLY:
        return TOWNSQUARE_IMAGE.format(role_id=role_id)

    return TOWNSQUARE_IMAGE.format(role_id=role_id)


def patch_characters_en(*, data_dir: Path = DATA_DIR) -> list[dict[str, object]]:
    characters_en = load_json(data_dir / "characters-en.json")
    role_editions = load_json(data_dir / "role-editions.json")

    if not isinstance(characters_en, list):
        raise ValueError("characters-en.json must be a JSON array")
    if not isinstance(role_editions, dict):
        raise ValueError("role-editions.json must be a JSON object")

    patched = 0
    for entry in characters_en:
        role_id = entry["id"]
        resolved_edition = role_editions.get(role_id)

        if not entry.get("edition") and resolved_edition and resolved_edition != "fabled":
            entry["edition"] = resolved_edition
            patched += 1

        image = community_image_url(role_id, entry.get("team", ""), resolved_edition)
        if entry.get("image") != image:
            entry["image"] = image
            patched += 1
            print(f"image {role_id} -> {image}", file=sys.stderr)

    print(f"Patched {patched} fields", file=sys.stderr)
    return characters_en


def main() -> int:
    characters_en = patch_characters_en()
    output = DATA_DIR / "characters-en.json"
    output.write_text(
        json.dumps(characters_en, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(characters_en)} characters to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
