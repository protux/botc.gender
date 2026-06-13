import "./style.css";
import { convertScript, loadDataStore } from "./lib/convert";
import { scriptToolUrl } from "./lib/scriptToolUrl";
import type { Strategy } from "./lib/strategies";

interface AppState {
  converted: unknown[] | null;
}

const state: AppState = {
  converted: null,
};

const app = document.querySelector<HTMLDivElement>("#app")!;

app.innerHTML = `
  <main>
    <header>
      <h1>botc.gender</h1>
      <p>
        Konvertiert Blood-on-the-Clocktower-Script-JSON in vollständige,
        gegenderte deutsche Script-Dateien – direkt im Browser, ohne Upload.
      </p>
    </header>

    <section class="panel">
      <label for="input-json">Script-JSON</label>
      <textarea
        id="input-json"
        placeholder='Füge hier das JSON aus dem offiziellen Script Tool ein …'
        spellcheck="false"
      ></textarea>

      <div class="options">
        <div class="field">
          <label for="strategy">Strategie</label>
          <select id="strategy">
            <option value="official-override">official-override (Script Tool)</option>
            <option value="custom-suffix">custom-suffix (Bloodstar, Huwig, …)</option>
          </select>
        </div>

        <div class="field checkbox-field">
          <input id="official-images" type="checkbox" checked />
          <label for="official-images">Offizielle Bilder (release.botc.app)</label>
        </div>
      </div>

      <div class="actions">
        <button id="convert" class="primary" type="button">Konvertieren</button>
        <a id="open-script-tool" class="button-link primary disabled" href="#" target="_blank" rel="noopener">
          Open in Script Tool
        </a>
        <button id="download-json" class="secondary" type="button" disabled>
          JSON herunterladen
        </button>
      </div>

      <div id="status" class="status" aria-live="polite"></div>
      <p class="hint">
        Für das offizielle Script Tool wird <strong>official-override</strong> empfohlen.
        Der Button öffnet script.bloodontheclocktower.com mit dem gegenderten Script.
      </p>
    </section>

    <footer>
      <p>
        CLI und Datenquellen:
        <a href="https://github.com/ThePandemoniumInstitute/botc-translations">botc-translations</a>
      </p>
    </footer>
  </main>
`;

const input = document.querySelector<HTMLTextAreaElement>("#input-json")!;
const strategySelect = document.querySelector<HTMLSelectElement>("#strategy")!;
const officialImages = document.querySelector<HTMLInputElement>("#official-images")!;
const convertButton = document.querySelector<HTMLButtonElement>("#convert")!;
const openScriptTool = document.querySelector<HTMLAnchorElement>("#open-script-tool")!;
const downloadButton = document.querySelector<HTMLButtonElement>("#download-json")!;
const status = document.querySelector<HTMLDivElement>("#status")!;

let dataStore: Awaited<ReturnType<typeof loadDataStore>> | null = null;

function setStatus(message: string, kind: "success" | "error" | "" = "") {
  status.textContent = message;
  status.className = kind ? `status ${kind}` : "status";
}

function resetResultUi() {
  state.converted = null;
  openScriptTool.classList.add("disabled");
  openScriptTool.href = "#";
  downloadButton.disabled = true;
}

function updateResultUi(result: unknown[]) {
  state.converted = result;
  const meta = result[0] as Record<string, unknown>;
  const roleCount = result.length - 1;
  const scriptName = typeof meta.name === "string" ? meta.name : "Script";

  openScriptTool.href = scriptToolUrl(result);
  openScriptTool.classList.remove("disabled");
  downloadButton.disabled = false;

  setStatus(
    `${roleCount} Rollen konvertiert (${scriptName}).`,
    "success",
  );
}

function parseInputJson(raw: string): unknown[] {
  const parsed = JSON.parse(raw) as unknown;
  if (!Array.isArray(parsed)) {
    throw new Error("Das JSON muss ein Array sein.");
  }
  return parsed;
}

async function ensureStore() {
  if (dataStore) {
    return dataStore;
  }
  setStatus("Lade Rollendaten …");
  dataStore = await loadDataStore();
  setStatus("");
  return dataStore;
}

async function handleConvert() {
  resetResultUi();

  const rawText = input.value.trim();
  if (!rawText) {
    setStatus("Bitte zuerst Script-JSON einfügen.", "error");
    return;
  }

  convertButton.disabled = true;

  try {
    const store = await ensureStore();
    const raw = parseInputJson(rawText);
    const result = convertScript(store, raw, {
      strategy: strategySelect.value as Strategy,
      useOfficialImages: officialImages.checked,
    });
    updateResultUi(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unbekannter Fehler";
    setStatus(message, "error");
  } finally {
    convertButton.disabled = false;
  }
}

function handleDownload() {
  if (!state.converted) {
    return;
  }

  const meta = state.converted[0] as Record<string, unknown>;
  const slug =
    typeof meta.name === "string"
      ? meta.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")
      : "script";

  const blob = new Blob([JSON.stringify(state.converted, null, 2) + "\n"], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${slug || "script"}-de-gendered.json`;
  link.click();
  URL.revokeObjectURL(url);
}

convertButton.addEventListener("click", () => {
  void handleConvert();
});

downloadButton.addEventListener("click", handleDownload);

input.addEventListener("input", () => {
  resetResultUi();
  setStatus("");
});

strategySelect.addEventListener("change", resetResultUi);
officialImages.addEventListener("change", resetResultUi);

void ensureStore().catch((error) => {
  const message = error instanceof Error ? error.message : "Daten konnten nicht geladen werden.";
  setStatus(message, "error");
});
