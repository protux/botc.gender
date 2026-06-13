export type Strategy = "official-override" | "custom-suffix";

export function resolveRoleId(
  roleId: string,
  strategy: Strategy,
  suffix = "_de",
): string {
  if (strategy === "official-override") {
    return roleId;
  }
  return `${roleId}${suffix}`;
}
