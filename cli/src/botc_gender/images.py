from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

OFFICIAL_IMAGE_BASE = "https://release.botc.app/resources/characters"
PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parent.parent.parent
DATA_DIR = REPO_ROOT / "data"


@lru_cache(maxsize=1)
def _load_role_editions() -> dict[str, str | None]:
    path = DATA_DIR / "role-editions.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}
    return payload


def resolve_edition(*, role_id: str, edition: str, team: str) -> str | None:
    if edition:
        return edition

    resolved = _load_role_editions().get(role_id)
    if resolved:
        return resolved

    return None


def official_image_urls(*, role_id: str, edition: str, team: str) -> list[str] | None:
    """Build official character icon URLs from release.botc.app."""
    edition_key = resolve_edition(role_id=role_id, edition=edition, team=team)

    if edition_key == "fabled":
        return [f"{OFFICIAL_IMAGE_BASE}/fabled/{role_id}.webp"]

    if not edition_key:
        return None

    base = f"{OFFICIAL_IMAGE_BASE}/{edition_key}/{role_id}"

    if team == "traveller":
        return [f"{base}.webp", f"{base}_g.webp", f"{base}_e.webp"]

    if team in ("minion", "demon"):
        return [f"{base}_e.webp", f"{base}_g.webp"]

    return [f"{base}_g.webp", f"{base}_e.webp"]
