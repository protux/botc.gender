from __future__ import annotations

import pytest

from botc_gender.images import official_image_urls


@pytest.mark.parametrize(
    ("role_id", "edition", "team", "expected"),
    [
        (
            "librarian",
            "tb",
            "townsfolk",
            [
                "https://release.botc.app/resources/characters/tb/librarian_g.webp",
                "https://release.botc.app/resources/characters/tb/librarian_e.webp",
            ],
        ),
        (
            "shugenja",
            "carousel",
            "townsfolk",
            [
                "https://release.botc.app/resources/characters/carousel/shugenja_g.webp",
                "https://release.botc.app/resources/characters/carousel/shugenja_e.webp",
            ],
        ),
        (
            "imp",
            "tb",
            "demon",
            [
                "https://release.botc.app/resources/characters/tb/imp_e.webp",
                "https://release.botc.app/resources/characters/tb/imp_g.webp",
            ],
        ),
        (
            "beggar",
            "tb",
            "traveller",
            [
                "https://release.botc.app/resources/characters/tb/beggar.webp",
                "https://release.botc.app/resources/characters/tb/beggar_g.webp",
                "https://release.botc.app/resources/characters/tb/beggar_e.webp",
            ],
        ),
        (
            "djinn",
            "fabled",
            "fabled",
            ["https://release.botc.app/resources/characters/fabled/djinn.webp"],
        ),
        (
            "stormcatcher",
            "",
            "fabled",
            None,
        ),
    ],
)
def test_official_image_urls(role_id, edition, team, expected):
    assert official_image_urls(role_id=role_id, edition=edition, team=team) == expected
