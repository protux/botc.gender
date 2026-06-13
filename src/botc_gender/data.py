from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
GENDER_DIR = DATA_DIR / "gender"


@dataclass
class GenderConfig:
    replacements: list[tuple[re.Pattern[str], str]] = field(default_factory=list)
    pronouns: list[tuple[re.Pattern[str], str]] = field(default_factory=list)
    keep_gendered_roles: set[str] = field(default_factory=set)
    neutral_roles: set[str] = field(default_factory=set)
    overrides: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class DataStore:
    de_official: dict[str, Any]
    characters_en: dict[str, dict[str, Any]]
    characters_de_community: dict[str, dict[str, Any]]
    reminder_labels: dict[str, str]
    gender: GenderConfig


def _load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_gender_config(gender_dir: Path = GENDER_DIR) -> GenderConfig:
    raw_replacements = _load_yaml(gender_dir / "replacements.yaml") or []
    replacements: list[tuple[re.Pattern[str], str]] = []
    for entry in raw_replacements:
        replacements.append(
            (re.compile(entry["pattern"]), entry["replacement"])
        )

    keep_entries = _load_yaml(gender_dir / "keep-gendered-roles.yaml") or []
    keep_gendered_roles = {entry["id"] for entry in keep_entries}

    neutral_entries = _load_yaml(gender_dir / "neutral-roles.yaml") or []
    neutral_roles = {entry["id"] for entry in neutral_entries}

    overrides = _load_yaml(gender_dir / "overrides.yaml") or {}

    raw_pronouns = _load_yaml(gender_dir / "pronouns.yaml") or []
    pronouns: list[tuple[re.Pattern[str], str]] = []
    for entry in raw_pronouns:
        pronouns.append((re.compile(entry["pattern"]), entry["replacement"]))

    return GenderConfig(
        replacements=replacements,
        pronouns=pronouns,
        keep_gendered_roles=keep_gendered_roles,
        neutral_roles=neutral_roles,
        overrides=overrides,
    )


@lru_cache(maxsize=1)
def load_data_store(data_dir: Path = DATA_DIR) -> DataStore:
    de_official = _load_json(data_dir / "de-official.json")
    characters_en_list = _load_json(data_dir / "characters-en.json")
    characters_en = {item["id"]: item for item in characters_en_list}

    community_list = _load_json(data_dir / "characters-de-community.json")
    characters_de_community = {item["id"]: item for item in community_list}

    reminder_labels = de_official.get("reminders", {})

    return DataStore(
        de_official=de_official,
        characters_en=characters_en,
        characters_de_community=characters_de_community,
        reminder_labels=reminder_labels,
        gender=load_gender_config(data_dir / "gender"),
    )


def get_de_role(store: DataStore, role_id: str) -> dict[str, Any]:
    roles = store.de_official.get("roles", {})
    if role_id not in roles:
        raise KeyError(f"No German translation for role '{role_id}'")
    return roles[role_id]


def get_en_role(store: DataStore, role_id: str) -> dict[str, Any]:
    if role_id not in store.characters_en:
        raise KeyError(f"No English metadata for role '{role_id}'")
    return store.characters_en[role_id]
