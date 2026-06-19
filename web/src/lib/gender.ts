import type { DataStore, GenderConfig } from "./data";

const FEMININE_NAME_SUFFIXES = [
  "in",
  "frau",
  "mutter",
  "dame",
  "kind",
  "hexe",
  "witwe",
] as const;

const DOUBLE_GENDER_PATTERNS: Array<[RegExp, string]> = [
  [/:in:innen\b/g, ":innen"],
  [/:in:in\b/g, ":in"],
  [/\bSpieler:in:\s/g, "Spieler:in. "],
  [/\bSpieler:innen:\s/g, "Spieler:innen. "],
];

const NUMBERED_SPIELER_COLON = /\b(\d+)\s+Spieler:/g;
const PLURAL_SPIELER_IN = /\b(\d+)\s+Spieler:in\b/g;

function fixNumberedSpielerColon(text: string): string {
  return text.replace(NUMBERED_SPIELER_COLON, (_match, count: string) => {
    const n = Number.parseInt(count, 10);
    const form = n === 1 ? "Spieler:in" : "Spieler:innen";
    return `${n} ${form}.`;
  });
}

function fixPluralSpielerIn(text: string): string {
  return text.replace(PLURAL_SPIELER_IN, (match, count: string) => {
    const n = Number.parseInt(count, 10);
    if (n === 1) {
      return match;
    }
    return `${n} Spieler:innen`;
  });
}

function replaceWithBackrefs(
  text: string,
  pattern: RegExp,
  replacement: string,
): string {
  return text.replace(pattern, (...args) => {
    const groups = args.slice(1, -2) as string[];
    return replacement.replace(/\\(\d+)/g, (_match, index: string) => {
      const group = groups[Number.parseInt(index, 10) - 1];
      return group ?? "";
    });
  });
}

export function applyReplacements(text: string, config: GenderConfig): string {
  if (!text) {
    return text;
  }
  let result = fixNumberedSpielerColon(text);
  for (const [pattern, replacement] of config.replacements) {
    result = replaceWithBackrefs(result, pattern, replacement);
  }
  result = fixPluralSpielerIn(result);
  for (const [pattern, replacement] of config.pronouns) {
    result = replaceWithBackrefs(result, pattern, replacement);
  }
  for (const [pattern, replacement] of DOUBLE_GENDER_PATTERNS) {
    result = result.replace(pattern, replacement);
  }
  return result;
}

export function genderRoleName(
  roleId: string,
  name: string,
  config: GenderConfig,
): string {
  const override = config.overrides[roleId]?.name;
  if (override) {
    return String(override);
  }

  if (
    config.keepGenderedRoles.has(roleId) ||
    config.neutralRoles.has(roleId)
  ) {
    return name;
  }

  if (name.includes(":")) {
    return name;
  }

  const lower = name.toLowerCase();
  if (lower.includes(" frau") || FEMININE_NAME_SUFFIXES.some((suffix) => lower.endsWith(suffix))) {
    return name;
  }

  return `${name}:in`;
}

export function genderTextFields(
  roleId: string,
  fields: Record<string, unknown>,
  config: GenderConfig,
  options: { genderName: boolean },
): Record<string, unknown> {
  const result = { ...fields };
  const overrides = config.overrides[roleId] ?? {};

  if (options.genderName && "name" in result) {
    result.name = genderRoleName(roleId, String(result.name ?? ""), config);
  }

  for (const key of [
    "ability",
    "firstNightReminder",
    "otherNightReminder",
    "flavor",
  ] as const) {
    if (!(key in result) || result[key] == null) {
      continue;
    }
    if (key in overrides) {
      result[key] = overrides[key];
    } else {
      result[key] = applyReplacements(String(result[key]), config);
    }
  }

  if ("reminders" in result && Array.isArray(result.reminders)) {
    if ("reminders" in overrides) {
      result.reminders = overrides.reminders;
    } else {
      result.reminders = result.reminders.map((label) =>
        applyReplacements(String(label), config),
      );
    }
  }

  return result;
}

export function buildGenderedRoleTexts(
  store: DataStore,
  roleId: string,
): Record<string, unknown> {
  const deRole = store.deOfficial.roles[roleId] as Record<string, unknown>;
  const enRole = store.charactersEn[roleId];
  const community = store.charactersDeCommunity[roleId] ?? {};

  let reminders = community.reminders as string[] | undefined;
  if (!reminders && enRole.reminders) {
    reminders = enRole.reminders.map(
      (token) => store.reminderLabels[token] ?? token,
    );
  }

  const fields: Record<string, unknown> = {
    name: deRole.name ?? enRole.name,
    ability: deRole.ability ?? community.ability ?? enRole.ability,
    firstNightReminder:
      deRole.first ??
      community.firstNightReminder ??
      enRole.firstNightReminder ??
      "",
    otherNightReminder:
      deRole.other ??
      community.otherNightReminder ??
      enRole.otherNightReminder ??
      "",
    flavor: deRole.flavor ?? enRole.flavor ?? "",
  };
  if (reminders) {
    fields.reminders = reminders;
  }

  const genderName = !store.gender.keepGenderedRoles.has(roleId);
  return genderTextFields(roleId, fields, store.gender, { genderName });
}
