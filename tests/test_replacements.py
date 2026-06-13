from __future__ import annotations

import pytest

from botc_gender.data import load_gender_config
from botc_gender.gender import apply_replacements


@pytest.fixture
def config():
    return load_gender_config()


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("1 von 2 Spielern", "1 von 2 Spieler:innen"),
        ("der erste Spieler wählt", "der erste Spieler:in wählt"),
        ("Wähle jede Nacht 2 Spieler: Du erfährst", "Wähle jede Nacht 2 Spieler:innen. Du erfährst"),
        ("wähle öffentlich 1 Spieler: Falls er der Dämon ist, stirbt er.", "wähle öffentlich 1 Spieler:in. Falls die Person der Dämon ist, stirbt die Person."),
        ("Spieler:innen bleiben", "Spieler:innen bleiben"),
        ("Spieler:in:innen", "Spieler:innen"),
    ],
)
def test_no_double_gendering(config, source, expected):
    assert apply_replacements(source, config) == expected
