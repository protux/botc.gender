const LOCAL = "botc-gender";
const DOMAIN = ["nischwan", "de"] as const;

export function buildContactEmail(): string {
  return `${LOCAL}@${DOMAIN.join(".")}`;
}

export function buildMailtoHref(): string {
  return `mailto:${buildContactEmail()}`;
}

export const contactFallbackText = `${LOCAL} [at] ${DOMAIN[0]} [dot] ${DOMAIN[1]}`;
