import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it, beforeAll } from "vitest";
import {
  buildGenderConfig,
  convertScript,
  createDataStore,
  type DataStore,
} from "./convert";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const dataDir = resolve(repoRoot, "data");
const genderDir = resolve(dataDir, "gender");

let store: DataStore;

function readData(path: string): string {
  return readFileSync(path, "utf-8");
}

beforeAll(() => {
  store = createDataStore({
    deOfficial: JSON.parse(readData(resolve(dataDir, "de-official.json"))),
    charactersEnList: JSON.parse(readData(resolve(dataDir, "characters-en.json"))),
    communityList: JSON.parse(readData(resolve(dataDir, "characters-de-community.json"))),
    gender: buildGenderConfig({
      replacementsText: readData(resolve(genderDir, "replacements.yaml")),
      keepText: readData(resolve(genderDir, "keep-gendered-roles.yaml")),
      neutralText: readData(resolve(genderDir, "neutral-roles.yaml")),
      overridesText: readData(resolve(genderDir, "overrides.yaml")),
      pronounsText: readData(resolve(genderDir, "pronouns.yaml")),
    }),
  });
});

function loadFixture(name: string): unknown[] {
  const path = resolve(repoRoot, "cli/tests/fixtures", name);
  return JSON.parse(readData(path));
}

describe("gender conversion", () => {
  it("genders librarian ability text", () => {
    const raw = loadFixture("everyone-can-play.json");
    const result = convertScript(store, raw, { strategy: "official-override" });
    const librarian = result.find(
      (entry) =>
        typeof entry === "object" &&
        entry !== null &&
        (entry as Record<string, unknown>).id === "librarian",
    ) as Record<string, string>;

    expect(librarian.name).toBe("Bibliothekar:in");
    expect(librarian.ability).toContain("1 von 2 Spieler:innen");
    expect(librarian.ability).not.toContain(":in:innen");
    expect(librarian.ability).not.toContain("Spielern");
  });

  it("uses custom suffix strategy by default", () => {
    const raw = loadFixture("everyone-can-play.json");
    const result = convertScript(store, raw);
    expect((result[1] as Record<string, string>).id).toBe("librarian_de");
  });

  it("uses official ids with official-override", () => {
    const raw = loadFixture("everyone-can-play.json");
    const result = convertScript(store, raw, { strategy: "official-override" });
    const ids = result.slice(1).map((entry) => (entry as Record<string, string>).id);
    expect(ids[0]).toBe("librarian");
    expect(ids.every((id) => !id.includes("_de"))).toBe(true);
  });

  it("uses release.botc.app images when requested", () => {
    const raw = loadFixture("everyone-can-play.json");
    const result = convertScript(store, raw, { useOfficialImages: true });
    const librarian = result.find(
      (entry) =>
        typeof entry === "object" &&
        entry !== null &&
        (entry as Record<string, unknown>).id === "librarian_de",
    ) as Record<string, string[]>;

    expect(librarian.image).toEqual([
      "https://release.botc.app/resources/characters/tb/librarian_g.webp",
      "https://release.botc.app/resources/characters/tb/librarian_e.webp",
    ]);
  });
});
