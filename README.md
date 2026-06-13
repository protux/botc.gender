# botc.gender

Konvertiert Blood-on-the-Clocktower-Script-JSON (nur Charakter-IDs) in vollständige, **gegenderte deutsche** Script-Dateien für Druck und digitale Tools.

## Web-App

Die statische Web-App liegt in [`web/`](web/). Sie läuft vollständig im Browser – kein Upload, keine Server-Logik.

```bash
cd web
npm install
npm run dev
```

Nach der Konvertierung:

- **Open in Script Tool** – öffnet [script.bloodontheclocktower.com](https://script.bloodontheclocktower.com/) mit dem gegenderten Script (gzip + Base64 in der URL, wie bei [botcscripts.com](https://www.botcscripts.com/))
- **JSON herunterladen** – optional

Deployment auf GitHub Pages: Workflow [`.github/workflows/deploy-web.yml`](.github/workflows/deploy-web.yml). In den Repository-Einstellungen **Pages → Source: GitHub Actions** aktivieren.

## CLI

Das Python-CLI liegt in [`cli/`](cli/).

### Installation

```bash
cd botc.gender
pip install -e "cli/[dev]"
```

### Schnellstart

```bash
# Standard: gegenderte Custom-Rollen (librarian_de, …) mit offiziellen Bildern
botc-gender convert cli/tests/fixtures/everyone-can-play.json \
  -o output/everyone-de-gendered.json \
  --official

# Workaround fürs offizielle Script-Tool (offizielle IDs, gegenderte Texte)
botc-gender convert cli/tests/fixtures/everyone-can-play.json \
  -o output/everyone-de-official-ids.json \
  --strategy official-override \
  --official
```

## Workflow

1. Script im [offiziellen Tool](https://script.bloodontheclocktower.com/) erstellen → JSON exportieren
2. In der Web-App konvertieren **oder** mit `botc-gender convert` erzeugen
3. „Open in Script Tool“ nutzen **oder** JSON im gewünschten PDF-Tool importieren

## Strategien

| Strategie | Charakter-IDs | Für |
|-----------|---------------|-----|
| `custom-suffix` (CLI-Standard) | Custom IDs (`librarian_de`) | Bloodstar, unofficial Script Tool, Huwig, clocktower.online |
| `official-override` | Offizielle IDs (`librarian`) | Offizielles Script Tool (Web-Standard) |

`--official` / „Offizielle Bilder“ betrifft **nur die Bilder** — die Charakter-IDs bleiben von der gewählten Strategie.

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

## Gender-Regeln

Konfiguration in `data/gender/`:

- `replacements.yaml` — Wortersetzungen (z. B. `Spieler` → `Spieler:in`)
- `keep-gendered-roles.yaml` — Rollen mit explizitem Geschlecht im Namen (z. B. Großmutter, Scharlachrote Frau)
- `neutral-roles.yaml` — Neutrale/Anglizismen (z. B. Imp, Empath)
- `overrides.yaml` — Manuelle Korrekturen pro Rolle

## Daten aktualisieren

```bash
./cli/scripts/update_data.sh
cd web && npm run sync-data
```

Quellen:

- [TPI botc-translations/game/de.json](https://github.com/ThePandemoniumInstitute/botc-translations) — offizielle deutsche Texte
- [TPI botc-translations/game/en.json](https://github.com/ThePandemoniumInstitute/botc-translations) — offizielle englische Texte (Ergänzung fehlender Rollen)
- [RealVidy botc-translations](https://github.com/RealVidy/botc-translations) — Metadaten und Fallback-Reminder

`scripts/merge_characters_en.py` ergänzt Rollen, die in RealVidy fehlen (z. B. `shugenja`), anhand der TPI-Texte und Wiki-Typen. Anschließend setzen `build_role_editions.py` und `patch_characters_en.py` fehlende Editionen und Bild-URLs (Carousel/Fabled auf release.botc.app).

## Tests

```bash
pytest cli/tests
cd web && npm test
```
