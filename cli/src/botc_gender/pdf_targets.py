from __future__ import annotations

from typing import Literal

PdfTarget = Literal[
    "official-tool",
    "unofficial-script-tool",
    "huwig",
    "scriptmaker",
]

PDF_TARGET_INFO: dict[PdfTarget, dict[str, str]] = {
    "official-tool": {
        "title": "Offizielles Script Tool",
        "url": "https://script.bloodontheclocktower.com/",
        "strategy": "official-override",
        "steps": (
            "1. JSON mit --strategy official-override erzeugen.\n"
            "2. Auf script.bloodontheclocktower.com importieren (Upload-Button).\n"
            "3. Prüfen, ob gegenderte Namen/Fähigkeiten angezeigt werden.\n"
            "4. Über Druck/Export das PDF erzeugen.\n"
            "Hinweis: Das Tool unterstützt offiziell keine Homebrew-Rollen; "
            "official-override nutzt dieselben Charakter-IDs mit überschriebenen Texten."
        ),
    },
    "unofficial-script-tool": {
        "title": "Unofficial Script Tool (Conor Reynolds)",
        "url": "https://creynolds.ie/botc-script-tool",
        "strategy": "custom-suffix",
        "steps": (
            "1. JSON mit --strategy custom-suffix erzeugen.\n"
            "2. Auf creynolds.ie/botc-script-tool importieren.\n"
            "3. Nacht-Reihenfolge bei Bedarf anpassen.\n"
            "4. Drucken → PDF (zwei Spalten, kompaktes Nachtblatt optional)."
        ),
    },
    "huwig": {
        "title": "Huwig – Deutsche Spielerblätter",
        "url": "https://www.huwig.de/clocktower/deutsche-spielerblaetter-fuer-blood-on-the-clocktower/",
        "strategy": "custom-suffix",
        "steps": (
            "1. JSON mit --strategy custom-suffix erzeugen.\n"
            "2. JSON in das Formular auf huwig.de einfügen.\n"
            "3. Sprache „German“ wählen, ggf. „include English names“ deaktivieren.\n"
            "4. Seite drucken oder als PDF speichern (Skalierung anpassen)."
        ),
    },
    "scriptmaker": {
        "title": "rsarvar1a/scriptmaker (CLI)",
        "url": "https://github.com/rsarvar1a/scriptmaker",
        "strategy": "custom-suffix",
        "steps": (
            "1. JSON mit --strategy custom-suffix erzeugen.\n"
            "2. scriptmaker installieren: pip install scriptmaker (falls verfügbar).\n"
            "3. scriptmaker build output.json --output-folder ./pdf\n"
            "4. PDF aus dem pdf/-Ordner drucken."
        ),
    },
}


def format_pdf_instructions(target: PdfTarget) -> str:
    info = PDF_TARGET_INFO[target]
    lines = [
        f"PDF-Ziel: {info['title']}",
        f"URL: {info['url']}",
        f"Empfohlene Strategie: {info['strategy']}",
        "",
        info["steps"],
    ]
    return "\n".join(lines)
