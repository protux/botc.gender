const OFFICIAL_IMAGE_BASE = "https://release.botc.app/resources/characters";

let roleEditions: Record<string, string | null> | null = null;

async function loadRoleEditions(baseUrl: string): Promise<Record<string, string | null>> {
  if (roleEditions) {
    return roleEditions;
  }
  try {
    const response = await fetch(`${baseUrl}role-editions.json`);
    if (!response.ok) {
      roleEditions = {};
      return roleEditions;
    }
    roleEditions = (await response.json()) as Record<string, string | null>;
  } catch {
    roleEditions = {};
  }
  return roleEditions!;
}

export async function initRoleEditions(baseUrl = `${import.meta.env.BASE_URL}data/`): Promise<void> {
  await loadRoleEditions(baseUrl);
}

export function resolveEdition(roleId: string, edition: string, _team: string): string | null {
  if (edition) {
    return edition;
  }
  const resolved = roleEditions?.[roleId];
  if (resolved) {
    return resolved;
  }
  return null;
}

export function officialImageUrls(
  roleId: string,
  edition: string,
  team: string,
): string[] | null {
  const editionKey = resolveEdition(roleId, edition, team);

  if (editionKey === "fabled") {
    return [`${OFFICIAL_IMAGE_BASE}/fabled/${roleId}.webp`];
  }

  if (!editionKey) {
    return null;
  }

  const base = `${OFFICIAL_IMAGE_BASE}/${editionKey}/${roleId}`;

  if (team === "traveller") {
    return [`${base}.webp`, `${base}_g.webp`, `${base}_e.webp`];
  }

  if (team === "minion" || team === "demon") {
    return [`${base}_e.webp`, `${base}_g.webp`];
  }

  return [`${base}_g.webp`, `${base}_e.webp`];
}
