from __future__ import annotations

import json
from pathlib import Path

import pytest

from botc_gender.convert import convert_script
from botc_gender.data import load_data_store
from botc_gender.gender import build_gendered_role_texts

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def store():
    return load_data_store()


def test_librarian_gendering(store):
    texts = build_gendered_role_texts(store, "librarian")
    assert texts["name"] == "Bibliothekar:in"
    assert "Spieler:in" in texts["ability"]
    assert "Spielern" not in texts["ability"]


def test_grandmother_keeps_name(store):
    texts = build_gendered_role_texts(store, "grandmother")
    assert texts["name"] == "Großmutter"


def test_scarletwoman_keeps_name(store):
    texts = build_gendered_role_texts(store, "scarletwoman")
    assert texts["name"] == "Scharlachrote Frau"


def test_convert_everyone_can_play_official(store):
    raw = json.loads((FIXTURES / "everyone-can-play.json").read_text(encoding="utf-8"))
    result = convert_script(store, raw, strategy="official-override")
    assert result[0]["id"] == "_meta"
    assert len(result) == 25
    ids = [entry["id"] for entry in result[1:]]
    assert ids[0] == "librarian"
    assert all("_de" not in role_id for role_id in ids)


def test_convert_everyone_can_play_custom_suffix(store):
    raw = json.loads((FIXTURES / "everyone-can-play.json").read_text(encoding="utf-8"))
    result = convert_script(store, raw, strategy="custom-suffix")
    ids = [entry["id"] for entry in result[1:]]
    assert ids[0] == "librarian_de"
    assert all(role_id.endswith("_de") for role_id in ids)


def test_all_script_roles_convert(store):
    raw = json.loads((FIXTURES / "everyone-can-play.json").read_text(encoding="utf-8"))
    result = convert_script(store, raw)
    for entry in result[1:]:
        assert entry["name"]
        assert entry["team"]
        assert entry["ability"]
        assert len(entry["name"]) <= 30
        assert len(entry["ability"]) <= 250


def test_cli_pdf_targets(capsys):
    from botc_gender.cli import main

    assert main(["pdf-targets"]) == 0
    captured = capsys.readouterr()
    assert "official-tool" in captured.out
    assert "huwig" in captured.out
