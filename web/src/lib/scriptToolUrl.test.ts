import { describe, expect, it } from "vitest";
import { scriptToolUrl } from "./scriptToolUrl";

describe("scriptToolUrl", () => {
  it("builds a gzip-base64 script tool link", () => {
    const script = [
      { id: "_meta", name: "Test", author: "Author" },
      { id: "imp", name: "Imp", team: "demon", ability: "Jede Nacht wählst du ein Opfer." },
    ];
    const url = scriptToolUrl(script);

    expect(url.startsWith("https://script.bloodontheclocktower.com?script=")).toBe(true);
    expect(url).toContain("H4sI");
  });
});
