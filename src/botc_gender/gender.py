from __future__ import annotations

import re
from typing import Any

from botc_gender.data import DataStore, GenderConfig

FEMININE_NAME_SUFFIXES = (
    "in",
    "frau",
    "mutter",
    "dame",
    "kind",
    "hexe",
    "witwe",
)


def apply_replacements(text: str, config: GenderConfig) -> str:
    if not text:
        return text
    result = text
    for pattern, replacement in config.replacements:
        result = pattern.sub(replacement, result)
    return result


def gender_role_name(role_id: str, name: str, config: GenderConfig) -> str:
    override = config.overrides.get(role_id, {}).get("name")
    if override:
        return override

    if role_id in config.keep_gendered_roles or role_id in config.neutral_roles:
        return name

    if ":" in name:
        return name

    lower = name.lower()
    if " frau" in lower or lower.endswith(FEMININE_NAME_SUFFIXES):
        return name

    return f"{name}:in"


def gender_text_fields(
    role_id: str,
    fields: dict[str, Any],
    config: GenderConfig,
    *,
    gender_name: bool,
) -> dict[str, Any]:
    result = dict(fields)
    overrides = config.overrides.get(role_id, {})

    if gender_name and "name" in result:
        result["name"] = gender_role_name(role_id, result["name"], config)

    for key in ("ability", "firstNightReminder", "otherNightReminder", "flavor"):
        if key not in result or result[key] is None:
            continue
        if key in overrides:
            result[key] = overrides[key]
        else:
            result[key] = apply_replacements(str(result[key]), config)

    if "reminders" in result and isinstance(result["reminders"], list):
        if "reminders" in overrides:
            result["reminders"] = overrides["reminders"]
        else:
            result["reminders"] = [
                apply_replacements(str(label), config) for label in result["reminders"]
            ]

    return result


def build_gendered_role_texts(
    store: DataStore,
    role_id: str,
) -> dict[str, Any]:
    de_role = store.de_official["roles"][role_id]
    en_role = store.characters_en[role_id]
    community = store.characters_de_community.get(role_id, {})

    reminders = community.get("reminders")
    if not reminders and en_role.get("reminders"):
        reminders = [
            store.reminder_labels.get(token, token)
            for token in en_role["reminders"]
        ]

    fields: dict[str, Any] = {
        "name": de_role.get("name", en_role["name"]),
        "ability": de_role.get("ability", community.get("ability", en_role["ability"])),
        "firstNightReminder": de_role.get(
            "first",
            community.get("firstNightReminder", en_role.get("firstNightReminder", "")),
        ),
        "otherNightReminder": de_role.get(
            "other",
            community.get("otherNightReminder", en_role.get("otherNightReminder", "")),
        ),
        "flavor": de_role.get("flavor", en_role.get("flavor", "")),
    }
    if reminders:
        fields["reminders"] = reminders

    gender_name = role_id not in store.gender.keep_gendered_roles
    return gender_text_fields(
        role_id,
        fields,
        store.gender,
        gender_name=gender_name,
    )
