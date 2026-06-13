# botc.gender

Konvertiert Blood-on-the-Clocktower-Script-JSON (nur Charakter-IDs) in vollständige, **gegenderte deutsche** Script-Dateien für Druck und digitale Tools.

## Installation

```bash
cd botc.gender
pip install -e ".[dev]"
```

## Schnellstart

```bash
botc-gender convert tests/fixtures/everyone-can-play.json \
  -o output/everyone-de-official.json \
  --strategy official-override

botc-gender convert tests/fixtures/everyone-can-play.json \
  -o output/everyone-de-bloodstar.json \
  --strategy custom-suffix \
  --pdf-target unofficial-script-tool
```

## Workflow

1. Script im [offiziellen Tool](https://script.bloodontheclocktower.com/) erstellen → JSON exportieren
2. Mit `botc-gender convert` gegendertes JSON erzeugen
3. JSON im gewünschten PDF-Tool importieren (siehe unten)

## Strategien

| Strategie | Charakter-IDs | Für |
|-----------|---------------|-----|
| `official-override` (Standard) | Offizielle IDs (`librarian`) | Workaround fürs offizielle Script-Tool |
| `custom-suffix` | Custom IDs (`librarian_de`) | Bloodstar, unofficial Script Tool, Huwig, clocktower.online |

## PDF-Ziele (`--pdf-target`)

```bash
botc-gender pdf-targets
```

| Ziel | URL | Empfohlene Strategie |
|------|-----|----------------------|
| `official-tool` | https://script.bloodontheclocktower.com/ | `official-override` |
| `unofficial-script-tool` | https://creynolds.ie/botc-script-tool | `custom-suffix` |
| `huwig` | https://www.huwig.de/clocktower/deutsche-spielerblaetter-fuer-blood-on-the-clocktower/ | `custom-suffix` |
| `scriptmaker` | https://github.com/rsarvar1a/scriptmaker | `custom-suffix` |

Beispiel mit Anleitung auf stderr:

```bash
botc-gender convert script.json -o out.json --pdf-target huwig
```

## Gender-Regeln

Konfiguration in `data/gender/`:

- `replacements.yaml` — Wortersetzungen (z. B. `Spieler` → `Spieler:in`)
- `keep-gendered-roles.yaml` — Rollen mit explizitem Geschlecht im Namen (z. B. Großmutter, Scharlachrote Frau)
- `neutral-roles.yaml` — Neutrale/Anglizismen (z. B. Imp, Empath)
- `overrides.yaml` — Manuelle Korrekturen pro Rolle

## Daten aktualisieren

```bash
./scripts/update_data.sh
```

Quellen:

- [TPI botc-translations/game/de.json](https://github.com/ThePandemoniumInstitute/botc-translations) — offizielle deutsche Texte
- [RealVidy botc-translations](https://github.com/RealVidy/botc-translations) — Metadaten und Fallback-Reminder

## Tests

```bash
pytest
```
