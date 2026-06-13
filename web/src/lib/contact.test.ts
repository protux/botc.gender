import { describe, expect, it } from "vitest";
import { buildContactEmail, buildMailtoHref, contactFallbackText } from "./contact";

describe("contact", () => {
  it("builds the contact email without storing it in HTML", () => {
    expect(buildContactEmail()).toBe("botc-gender@nischwan.de");
    expect(buildMailtoHref()).toBe("mailto:botc-gender@nischwan.de");
    expect(contactFallbackText).toBe("botc-gender [at] nischwan [dot] de");
  });
});
