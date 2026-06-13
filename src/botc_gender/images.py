from __future__ import annotations

OFFICIAL_IMAGE_BASE = "https://release.botc.app/resources/characters"


def official_image_urls(*, role_id: str, edition: str, team: str) -> str | list[str]:
    """Build official character icon URLs from release.botc.app."""
    edition_key = edition or "tb"
    base = f"{OFFICIAL_IMAGE_BASE}/{edition_key}/{role_id}"

    if team == "traveller":
        return [f"{base}.webp", f"{base}_g.webp", f"{base}_e.webp"]

    if team in ("minion", "demon"):
        return [f"{base}_e.webp", f"{base}_g.webp"]

    return [f"{base}_g.webp", f"{base}_e.webp"]
