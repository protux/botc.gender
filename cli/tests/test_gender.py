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
    assert "1 von 2 Spieler:innen" in texts["ability"]
    assert ":in:innen" not in texts["ability"]
    assert "Spielern" not in texts["ability"]


def test_fortuneteller_gendering(store):
    texts = build_gendered_role_texts(store, "fortuneteller")
    assert texts["name"] == "Wahrsager:in"
    assert "2 Spieler:innen." in texts["ability"]
    assert "Spieler:in:" not in texts["ability"]
    assert ", der dir" not in texts["ability"]


def test_empath_gendering(store):
    texts = build_gendered_role_texts(store, "empath")
    assert texts["name"] == "Empath:in"
    assert "Nachbar:innen" in texts["ability"]


def test_slayer_neutral_pronouns(store):
    texts = build_gendered_role_texts(store, "slayer")
    assert texts["name"] == "Dämonenjäger:in"
    assert "1 Spieler:in." in texts["ability"]
    assert "Falls die Person der Dämon ist, stirbt die Person." in texts["ability"]
    assert "Falls er" not in texts["ability"]


def test_monk_keeps_name_and_neutral_ability(store):
    texts = build_gendered_role_texts(store, "monk")
    assert texts["name"] == "Mönch"
    assert "Die Person ist heute Nacht sicher vor dem Dämon." in texts["ability"]
    assert " Er " not in texts["ability"]


def test_mayor_neutral_phrasing(store):
    texts = build_gendered_role_texts(store, "mayor")
    assert "3 Personen leben" in texts["ability"]
    assert "eine andere Person sterben" in texts["ability"]
    assert "Spieler" not in texts["ability"]


def test_moonchild_neutral_phrasing(store):
    texts = build_gendered_role_texts(store, "moonchild")
    assert texts["name"] == "Mondkind"
    assert "Falls die Person gut war" in texts["ability"]
    assert "ein guter" not in texts["ability"]


def test_devilsadvocate_and_spy_phrasing(store):
    devil = build_gendered_role_texts(store, "devilsadvocate")
    assert devil["name"] == "Teufelsadvokat"
    assert "1 andere:n als" in devil["ability"]

    spy = build_gendered_role_texts(store, "spy")
    assert "als ein:e Bürger:in oder Außenseiter:in" in spy["ability"]


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


def test_default_strategy_is_custom_suffix(store):
    raw = json.loads((FIXTURES / "everyone-can-play.json").read_text(encoding="utf-8"))
    result = convert_script(store, raw)
    assert result[1]["id"] == "librarian_de"


def test_official_images_use_release_botc_app(store):
    raw = json.loads((FIXTURES / "everyone-can-play.json").read_text(encoding="utf-8"))
    result = convert_script(store, raw, use_official_images=True)
    librarian = next(entry for entry in result if entry.get("id") == "librarian_de")
    imp = next(entry for entry in result if entry.get("id") == "imp_de")

    assert librarian["image"] == [
        "https://release.botc.app/resources/characters/tb/librarian_g.webp",
        "https://release.botc.app/resources/characters/tb/librarian_e.webp",
    ]
    assert imp["image"] == [
        "https://release.botc.app/resources/characters/tb/imp_e.webp",
        "https://release.botc.app/resources/characters/tb/imp_g.webp",
    ]


def test_default_images_use_community_source(store):
    raw = json.loads((FIXTURES / "everyone-can-play.json").read_text(encoding="utf-8"))
    result = convert_script(store, raw, use_official_images=False)
    librarian = next(entry for entry in result if entry.get("id") == "librarian_de")
    image = librarian["image"]
    if isinstance(image, list):
        image = image[0]
    assert "release.botc.app" in image

    raw = json.loads((FIXTURES / "everyone-can-play.json").read_text(encoding="utf-8"))
    result = convert_script(store, raw)
    for entry in result[1:]:
        assert entry["name"]
        assert entry["team"]
        assert entry["ability"]
        assert len(entry["name"]) <= 30
        assert len(entry["ability"]) <= 250


def test_noble_uses_adliger_name(store):
    texts = build_gendered_role_texts(store, "noble")
    assert texts["name"] == "Adlige:r"


def test_amnesiac_uses_vergesslicher_name(store):
    texts = build_gendered_role_texts(store, "amnesiac")
    assert texts["name"] == "Vergessliche:r"


def test_villageidiot_keeps_name(store):
    texts = build_gendered_role_texts(store, "villageidiot")
    assert texts["name"] == "Dorftrottel"
    assert "Dorftrottel:in" not in texts.get("ability", "")


@pytest.mark.parametrize("role_id,expected_name", [
    ("lilmonsta", "Lil' Monsta"),
    ("ojo", "Ojo"),
    ("savant", "Savant"),
    ("cerenovus", "Cerenovus"),
])
def test_neutral_role_names_unchanged(store, role_id, expected_name):
    texts = build_gendered_role_texts(store, role_id)
    assert texts["name"] == expected_name


def test_stormcatcher_script_images(store):
    raw = json.loads((FIXTURES / "stormcatcher-goon.json").read_text(encoding="utf-8"))
    result = convert_script(store, raw, strategy="official-override", use_official_images=True)
    shugenja = next(entry for entry in result if entry.get("id") == "shugenja")
    stormcatcher = next(entry for entry in result if entry.get("id") == "stormcatcher")

    assert shugenja["image"][0].endswith("/carousel/shugenja_g.webp")
    assert "stormcatcher" in stormcatcher["image"]


def test_shugenja_converts(store):
    raw = json.loads((FIXTURES / "shugenja.json").read_text(encoding="utf-8"))
    result = convert_script(store, raw, strategy="official-override")
    shugenja = next(entry for entry in result if entry.get("id") == "shugenja")
    assert shugenja["name"] == "Shugenja"
    assert "Spieler:in" in shugenja["ability"] or "Spieler:innen" in shugenja["ability"]


def test_cli_pdf_targets(capsys):
    from botc_gender.cli import main

    assert main(["pdf-targets"]) == 0
    captured = capsys.readouterr()
    assert "official-tool" in captured.out
    assert "huwig" in captured.out
