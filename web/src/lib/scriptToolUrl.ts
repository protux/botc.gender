import { gzip } from "pako";

const SCRIPT_TOOL_BASE = "https://script.bloodontheclocktower.com";

export function scriptToolUrl(script: unknown[]): string {
  const json = JSON.stringify(script);
  const compressed = gzip(json);
  const bytes = Uint8Array.from(compressed);
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  const base64 = btoa(binary);
  return `${SCRIPT_TOOL_BASE}?script=${encodeURIComponent(base64)}`;
}
