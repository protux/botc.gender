import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const source = resolve(root, "data");
const target = resolve(root, "web/public/data");

if (!existsSync(source)) {
  throw new Error(`Missing data directory: ${source}`);
}

mkdirSync(resolve(root, "web/public"), { recursive: true });
if (existsSync(target)) {
  rmSync(target, { recursive: true, force: true });
}
cpSync(source, target, { recursive: true });
console.log(`Synced ${source} -> ${target}`);
