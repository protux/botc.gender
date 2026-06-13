import yaml from "js-yaml";
import { buildGenderedRoleTexts } from "./gender";
import {
  buildCharacterObject,
  buildScriptArray,
} from "./appSchema";
import type { CharacterRecord, DataStore, GenderConfig } from "./data";
import type { Strategy } from "./strategies";

export type { CharacterRecord, DataStore, GenderConfig } from "./data";

async function fetchText(path: string): Promise<string> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to load ${path}: ${response.status}`);
  }
  return response.text();
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to load ${path}: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function loadYaml<T>(text: string): T {
  return (yaml.load(text) ?? {}) as T;
}

function compileRules(
  entries: Array<{ pattern: string; replacement: string }> | null | undefined,
): Array<[RegExp, string]> {
  return (entries ?? []).map((entry) => [
    new RegExp(entry.pattern),
    entry.replacement,
  ]);
}

export function buildGenderConfig(sources: {
  replacementsText: string;
  keepText: string;
  neutralText: string;
  overridesText: string;
  pronounsText: string;
}): GenderConfig {
  const keepEntries = loadYaml<Array<{ id: string }>>(sources.keepText) ?? [];
  const neutralEntries = loadYaml<Array<{ id: string }>>(sources.neutralText) ?? [];

  return {
    replacements: compileRules(
      loadYaml<Array<{ pattern: string; replacement: string }>>(sources.replacementsText),
    ),
    pronouns: compileRules(
      loadYaml<Array<{ pattern: string; replacement: string }>>(sources.pronounsText),
    ),
    keepGenderedRoles: new Set(keepEntries.map((entry) => entry.id)),
    neutralRoles: new Set(neutralEntries.map((entry) => entry.id)),
    overrides: loadYaml<Record<string, Record<string, unknown>>>(sources.overridesText) ?? {},
  };
}

export function createDataStore(input: {
  deOfficial: DataStore["deOfficial"];
  charactersEnList: CharacterRecord[];
  communityList: Array<Partial<CharacterRecord>>;
  gender: GenderConfig;
}): DataStore {
  const charactersEn = Object.fromEntries(
    input.charactersEnList.map((item) => [item.id, item]),
  );
  const charactersDeCommunity = Object.fromEntries(
    input.communityList.map((item) => [item.id!, item]),
  );

  return {
    deOfficial: input.deOfficial,
    charactersEn,
    charactersDeCommunity,
    reminderLabels: input.deOfficial.reminders ?? {},
    gender: input.gender,
  };
}

export async function loadGenderConfig(baseUrl: string): Promise<GenderConfig> {
  const genderBase = `${baseUrl}gender/`;
  const [
    replacementsText,
    keepText,
    neutralText,
    overridesText,
    pronounsText,
  ] = await Promise.all([
    fetchText(`${genderBase}replacements.yaml`),
    fetchText(`${genderBase}keep-gendered-roles.yaml`),
    fetchText(`${genderBase}neutral-roles.yaml`),
    fetchText(`${genderBase}overrides.yaml`),
    fetchText(`${genderBase}pronouns.yaml`),
  ]);

  return buildGenderConfig({
    replacementsText,
    keepText,
    neutralText,
    overridesText,
    pronounsText,
  });
}

export async function loadDataStore(baseUrl = `${import.meta.env.BASE_URL}data/`): Promise<DataStore> {
  const [deOfficial, charactersEnList, communityList, gender] = await Promise.all([
    fetchJson<DataStore["deOfficial"]>(`${baseUrl}de-official.json`),
    fetchJson<CharacterRecord[]>(`${baseUrl}characters-en.json`),
    fetchJson<Array<Partial<CharacterRecord>>>(`${baseUrl}characters-de-community.json`),
    loadGenderConfig(baseUrl),
  ]);

  return createDataStore({
    deOfficial,
    charactersEnList,
    communityList,
    gender,
  });
}

export function getDeRole(store: DataStore, roleId: string): Record<string, unknown> {
  const role = store.deOfficial.roles[roleId];
  if (!role) {
    throw new Error(`No German translation for role '${roleId}'`);
  }
  return role;
}

export function getEnRole(store: DataStore, roleId: string): CharacterRecord {
  const role = store.charactersEn[roleId];
  if (!role) {
    throw new Error(`No English metadata for role '${roleId}'`);
  }
  return role;
}

export function parseScriptInput(raw: unknown[]): {
  meta: Record<string, unknown>;
  roleIds: string[];
} {
  let meta: Record<string, unknown> | null = null;
  const roleIds: string[] = [];

  for (const entry of raw) {
    if (typeof entry === "object" && entry !== null && "id" in entry) {
      const record = entry as Record<string, unknown>;
      if (record.id === "_meta") {
        meta = { ...record };
      } else {
        roleIds.push(String(record.id));
      }
    } else if (typeof entry === "string") {
      roleIds.push(entry);
    }
  }

  if (!meta) {
    throw new Error("Script JSON must contain a _meta object");
  }
  if (roleIds.length === 0) {
    throw new Error("Script JSON contains no character IDs");
  }

  return { meta, roleIds };
}

export function convertScript(
  store: DataStore,
  rawScript: unknown[],
  options: {
    strategy?: Strategy;
    suffix?: string;
    useOfficialImages?: boolean;
  } = {},
): unknown[] {
  const strategy = options.strategy ?? "custom-suffix";
  const suffix = options.suffix ?? "_de";
  const useOfficialImages = options.useOfficialImages ?? false;

  const { meta, roleIds } = parseScriptInput(rawScript);
  const characters: Record<string, unknown>[] = [];

  for (const roleId of roleIds) {
    getDeRole(store, roleId);
    const metadata = getEnRole(store, roleId);
    const texts = buildGenderedRoleTexts(store, roleId);
    characters.push(
      buildCharacterObject(roleId, texts, metadata as unknown as Record<string, unknown>, {
        strategy,
        suffix,
        useOfficialImages,
      }),
    );
  }

  return buildScriptArray(meta, characters);
}
