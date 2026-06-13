#!/usr/bin/env python3
"""Probe release.botc.app and record the edition folder for each character."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
BASE = "https://release.botc.app/resources/characters"
EDITION_CANDIDATES = ("tb", "snv", "bmr", "carousel")


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def url_exists(url: str) -> bool:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status == 200
    except urllib.error.HTTPError:
        return False


def probe_official_edition(role_id: str, team: str) -> str | None:
    if team in {"fabled", "loric"}:
        if url_exists(f"{BASE}/fabled/{role_id}.webp"):
            return "fabled"
        return None

    for edition in EDITION_CANDIDATES:
        candidates = [
            f"{BASE}/{edition}/{role_id}_g.webp",
            f"{BASE}/{edition}/{role_id}_e.webp",
            f"{BASE}/{edition}/{role_id}.webp",
        ]
        if any(url_exists(url) for url in candidates):
            return edition

    return None


def build_role_editions(*, data_dir: Path = DATA_DIR) -> dict[str, str | None]:
    characters_en = load_json(data_dir / "characters-en.json")
    if not isinstance(characters_en, list):
        raise ValueError("characters-en.json must be a JSON array")

    editions: dict[str, str | None] = {}
    for entry in characters_en:
        role_id = entry["id"]
        team = entry.get("team", "")
        existing = entry.get("edition") or None
        if existing:
            editions[role_id] = existing
            continue
        editions[role_id] = probe_official_edition(role_id, team)
        if editions[role_id]:
            print(f"{role_id}: {editions[role_id]}", file=sys.stderr)

    return editions


def main() -> int:
    editions = build_role_editions()
    output = DATA_DIR / "role-editions.json"
    output.write_text(json.dumps(editions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    resolved = sum(1 for value in editions.values() if value)
    print(f"Wrote {resolved}/{len(editions)} resolved editions to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
