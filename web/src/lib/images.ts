const OFFICIAL_IMAGE_BASE = "https://release.botc.app/resources/characters";

export function officialImageUrls(
  roleId: string,
  edition: string,
  team: string,
): string[] {
  const editionKey = edition || "tb";
  const base = `${OFFICIAL_IMAGE_BASE}/${editionKey}/${roleId}`;

  if (team === "traveller") {
    return [`${base}.webp`, `${base}_g.webp`, `${base}_e.webp`];
  }

  if (team === "minion" || team === "demon") {
    return [`${base}_e.webp`, `${base}_g.webp`];
  }

  return [`${base}_g.webp`, `${base}_e.webp`];
}
