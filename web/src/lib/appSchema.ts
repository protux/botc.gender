import type { Strategy } from "./strategies";
import { resolveRoleId } from "./strategies";
import { officialImageUrls } from "./images";

export interface RoleTexts {
  name?: string;
  ability?: string;
  firstNightReminder?: string;
  otherNightReminder?: string;
  flavor?: string;
  reminders?: string[];
}

export function buildCharacterObject(
  roleId: string,
  texts: RoleTexts,
  metadata: Record<string, unknown>,
  options: {
    strategy: Strategy;
    suffix?: string;
    useOfficialImages?: boolean;
  },
): Record<string, unknown> {
  const outputId = resolveRoleId(roleId, options.strategy, options.suffix);
  const character: Record<string, unknown> = {
    id: outputId,
    name: String(texts.name ?? "").slice(0, 30),
    team: metadata.team,
    ability: String(texts.ability ?? "").slice(0, 250),
  };

  if (metadata.edition) {
    character.edition = metadata.edition;
  }
  if (options.useOfficialImages) {
    character.image = officialImageUrls(
      roleId,
      String(metadata.edition ?? ""),
      String(metadata.team ?? ""),
    );
  } else if (metadata.image) {
    character.image = metadata.image;
  }
  if (metadata.firstNight !== undefined && metadata.firstNight !== null) {
    character.firstNight = metadata.firstNight;
  }
  if (metadata.otherNight !== undefined && metadata.otherNight !== null) {
    character.otherNight = metadata.otherNight;
  }
  if (metadata.setup !== undefined && metadata.setup !== null) {
    character.setup = metadata.setup;
  }
  if (metadata.special) {
    character.special = metadata.special;
  }

  if (texts.firstNightReminder) {
    character.firstNightReminder = String(texts.firstNightReminder).slice(0, 500);
  }
  if (texts.otherNightReminder) {
    character.otherNightReminder = String(texts.otherNightReminder).slice(0, 500);
  }
  if (texts.flavor) {
    character.flavor = String(texts.flavor).slice(0, 500);
  }
  if (texts.reminders) {
    character.reminders = texts.reminders.map((item) => String(item).slice(0, 30)).slice(0, 20);
  }
  if (metadata.remindersGlobal) {
    character.remindersGlobal = metadata.remindersGlobal;
  }

  return character;
}

export function buildScriptArray(
  meta: Record<string, unknown>,
  characters: Record<string, unknown>[],
): unknown[] {
  return [meta, ...characters];
}
