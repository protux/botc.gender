from __future__ import annotations

from typing import Any

from botc_gender.formats.strategies.official_override import resolve_role_id
from botc_gender.formats.strategies.types import Strategy
from botc_gender.images import official_image_urls


def build_character_object(
    role_id: str,
    texts: dict[str, Any],
    metadata: dict[str, Any],
    *,
    strategy: Strategy,
    suffix: str = "_de",
    use_official_images: bool = False,
) -> dict[str, Any]:
    output_id = resolve_role_id(role_id, strategy, suffix)

    character: dict[str, Any] = {
        "id": output_id,
        "name": str(texts["name"])[:30],
        "team": metadata["team"],
        "ability": str(texts["ability"])[:250],
    }

    if metadata.get("edition"):
        character["edition"] = metadata["edition"]
    if use_official_images:
        character["image"] = official_image_urls(
            role_id=role_id,
            edition=str(metadata.get("edition", "")),
            team=metadata["team"],
        )
    elif metadata.get("image"):
        character["image"] = metadata["image"]
    if metadata.get("firstNight") is not None:
        character["firstNight"] = metadata["firstNight"]
    if metadata.get("otherNight") is not None:
        character["otherNight"] = metadata["otherNight"]
    if metadata.get("setup") is not None:
        character["setup"] = metadata["setup"]
    if metadata.get("special"):
        character["special"] = metadata["special"]

    if texts.get("firstNightReminder"):
        character["firstNightReminder"] = str(texts["firstNightReminder"])[:500]
    if texts.get("otherNightReminder"):
        character["otherNightReminder"] = str(texts["otherNightReminder"])[:500]
    if texts.get("flavor"):
        character["flavor"] = str(texts["flavor"])[:500]
    if texts.get("reminders"):
        character["reminders"] = [str(item)[:30] for item in texts["reminders"]][:20]
    if metadata.get("remindersGlobal"):
        character["remindersGlobal"] = metadata["remindersGlobal"]

    return character


def build_script_array(
    meta: dict[str, Any],
    characters: list[dict[str, Any]],
) -> list[Any]:
    return [meta, *characters]
