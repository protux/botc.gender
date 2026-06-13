from __future__ import annotations

from typing import Any

from botc_gender.data import DataStore, get_de_role, get_en_role
from botc_gender.formats.app_schema import Strategy, build_character_object, build_script_array
from botc_gender.gender import build_gendered_role_texts


def parse_script_input(raw: list[Any]) -> tuple[dict[str, Any], list[str]]:
    meta: dict[str, Any] | None = None
    role_ids: list[str] = []

    for entry in raw:
        if isinstance(entry, dict) and entry.get("id") == "_meta":
            meta = dict(entry)
        elif isinstance(entry, str):
            role_ids.append(entry)
        elif isinstance(entry, dict) and entry.get("id"):
            role_ids.append(entry["id"])

    if meta is None:
        raise ValueError("Script JSON must contain a _meta object")

    if not role_ids:
        raise ValueError("Script JSON contains no character IDs")

    return meta, role_ids


def convert_script(
    store: DataStore,
    raw_script: list[Any],
    *,
    strategy: Strategy = "custom-suffix",
    suffix: str = "_de",
    use_official_images: bool = False,
) -> list[Any]:
    meta, role_ids = parse_script_input(raw_script)
    characters: list[dict[str, Any]] = []

    for role_id in role_ids:
        get_de_role(store, role_id)
        get_en_role(store, role_id)
        texts = build_gendered_role_texts(store, role_id)
        metadata = get_en_role(store, role_id)
        characters.append(
            build_character_object(
                role_id,
                texts,
                metadata,
                strategy=strategy,
                suffix=suffix,
                use_official_images=use_official_images,
            )
        )

    return build_script_array(meta, characters)
