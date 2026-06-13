#!/usr/bin/env python3
"""Merge RealVidy character metadata with official TPI roles missing from en_GB.json."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"

TYPE_RE = re.compile(
    r"<td>Type</td>\s*<td>(?:\[\[Character Types[^\|]*\|([^\]]+)\]\]|([^<]+))</td>",
    re.I,
)

TEAM_OVERRIDES: dict[str, str] = {
    "dawn": "fabled",
    "dusk": "fabled",
    "demoninfo": "fabled",
    "minioninfo": "fabled",
    "godofug": "fabled",
}

TOWNSQUARE_IMAGE = (
    "https://github.com/bra1n/townsquare/blob/main/src/assets/icons/{role_id}.png?raw=true"
)


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def wiki_team(page_titles: list[str]) -> str | None:
    for title in page_titles:
        url = (
            "https://wiki.bloodontheclocktower.com/api.php?action=parse&page="
            + urllib.parse.quote(title)
            + "&prop=wikitext&format=json"
        )
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                payload = json.load(response)
        except OSError:
            continue

        if "error" in payload:
            continue

        text = payload["parse"]["wikitext"]["*"]
        match = TYPE_RE.search(text)
        if match:
            return (match.group(1) or match.group(2)).strip().lower()

        time.sleep(0.1)

    return None


def page_titles(role_id: str, en_name: str, de_name: str) -> list[str]:
    candidates = [en_name, de_name, role_id.replace("_", " ").title(), role_id.title()]
    seen: set[str] = set()
    titles: list[str] = []
    for candidate in candidates:
        key = candidate.strip().lower()
        if candidate and key not in seen:
            seen.add(key)
            titles.append(candidate)
    return titles


def build_supplement_entry(
    role_id: str,
    en_role: dict[str, object],
    team: str,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "id": role_id,
        "name": en_role.get("name", role_id),
        "team": team,
        "ability": en_role.get("ability", ""),
        "edition": "",
        "image": TOWNSQUARE_IMAGE.format(role_id=role_id),
        "firstNight": 0,
        "otherNight": 0,
        "firstNightReminder": en_role.get("first", ""),
        "otherNightReminder": en_role.get("other", ""),
        "reminders": [],
        "setup": False,
    }
    return entry


def merge_characters_en(
    *,
    data_dir: Path = DATA_DIR,
    fetch_wiki: bool = True,
) -> list[dict[str, object]]:
    de_official = load_json(data_dir / "de-official.json")
    en_official = load_json(data_dir / "en-official.json")
    characters_en = load_json(data_dir / "characters-en.json")

    if not isinstance(characters_en, list):
        raise ValueError("characters-en.json must be a JSON array")

    de_roles = de_official["roles"]
    en_roles = en_official["roles"]
    known_ids = {entry["id"] for entry in characters_en}

    supplements: list[dict[str, object]] = []
    for role_id in sorted(set(de_roles) - known_ids):
        en_role = en_roles.get(role_id)
        if not en_role:
            print(
                f"warning: no English official text for '{role_id}', skipping",
                file=sys.stderr,
            )
            continue

        team = TEAM_OVERRIDES.get(role_id)
        if not team and fetch_wiki:
            de_name = str(de_roles[role_id].get("name", ""))
            en_name = str(en_role.get("name", ""))
            team = wiki_team(page_titles(role_id, en_name, de_name))

        if not team:
            print(
                f"warning: could not resolve team for '{role_id}', skipping",
                file=sys.stderr,
            )
            continue

        supplements.append(build_supplement_entry(role_id, en_role, team))
        print(f"added {role_id} ({team})", file=sys.stderr)

    merged = characters_en + supplements
    merged.sort(key=lambda entry: entry["id"])
    return merged


def main() -> int:
    fetch_wiki = "--no-wiki" not in sys.argv
    merged = merge_characters_en(fetch_wiki=fetch_wiki)
    output = DATA_DIR / "characters-en.json"
    output.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(merged)} characters to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
