from __future__ import annotations

from botc_gender.formats.strategies.types import Strategy


def resolve_role_id(role_id: str, strategy: Strategy, suffix: str = "_de") -> str:
    if strategy == "official-override":
        return role_id
    return f"{role_id}{suffix}"
