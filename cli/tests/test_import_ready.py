from __future__ import annotations

import json
from pathlib import Path

import pytest

from botc_gender.convert import convert_script
from botc_gender.data import load_data_store
from botc_gender.pdf_targets import PDF_TARGET_INFO, format_pdf_instructions

FIXTURES = Path(__file__).parent / "fixtures"
OUTPUT = Path(__file__).parent.parent.parent / "output"


@pytest.fixture(scope="module")
def store():
    return load_data_store()


@pytest.fixture(scope="module")
def official_output(store):
    raw = json.loads((FIXTURES / "everyone-can-play.json").read_text(encoding="utf-8"))
    return convert_script(store, raw, strategy="official-override")


@pytest.fixture(scope="module")
def custom_output(store):
    raw = json.loads((FIXTURES / "everyone-can-play.json").read_text(encoding="utf-8"))
    return convert_script(store, raw, strategy="custom-suffix")


def test_official_import_shape(official_output):
    assert official_output[0]["id"] == "_meta"
    for entry in official_output[1:]:
        assert set(entry.keys()) >= {"id", "name", "team", "ability"}
        assert entry["team"] in {
            "townsfolk",
            "outsider",
            "minion",
            "demon",
            "traveller",
            "fabled",
            "loric",
        }
        assert len(entry["name"]) <= 30
        assert len(entry["ability"]) <= 250
        assert "_de" not in entry["id"]


def test_custom_import_shape(custom_output):
    ids = [entry["id"] for entry in custom_output[1:]]
    assert len(ids) == len(set(ids))
    assert all(role_id.endswith("_de") for role_id in ids)


def test_grandmother_ability_still_gendered(store):
    from botc_gender.gender import build_gendered_role_texts

    texts = build_gendered_role_texts(store, "grandmother")
    assert texts["name"] == "Großmutter"
    if "Spieler" in texts.get("ability", ""):
        assert "Spieler:in" in texts["ability"]


def test_written_outputs_exist_and_parse():
    for name in ("everyone-de-official.json", "everyone-de-custom.json"):
        path = OUTPUT / name
        assert path.exists(), f"Missing {path}; run botc-gender convert first"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) >= 2


@pytest.mark.parametrize("target", list(PDF_TARGET_INFO.keys()))
def test_pdf_target_instructions(target):
    text = format_pdf_instructions(target)
    assert PDF_TARGET_INFO[target]["url"] in text
    assert PDF_TARGET_INFO[target]["strategy"] in text
