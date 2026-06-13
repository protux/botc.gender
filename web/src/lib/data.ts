export interface GenderConfig {
  replacements: Array<[RegExp, string]>;
  pronouns: Array<[RegExp, string]>;
  keepGenderedRoles: Set<string>;
  neutralRoles: Set<string>;
  overrides: Record<string, Record<string, unknown>>;
}

export interface CharacterRecord {
  id: string;
  name: string;
  team: string;
  ability: string;
  edition?: string;
  image?: string | string[];
  firstNight?: number;
  otherNight?: number;
  setup?: boolean;
  special?: unknown;
  reminders?: string[];
  firstNightReminder?: string;
  otherNightReminder?: string;
  flavor?: string;
  remindersGlobal?: unknown;
}

export interface DataStore {
  deOfficial: {
    roles: Record<string, Record<string, unknown>>;
    reminders: Record<string, string>;
  };
  charactersEn: Record<string, CharacterRecord>;
  charactersDeCommunity: Record<string, Partial<CharacterRecord>>;
  reminderLabels: Record<string, string>;
  gender: GenderConfig;
}
