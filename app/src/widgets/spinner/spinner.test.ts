import { describe, expect, it } from "vitest";
import { createSpinner } from "./spinner.js";

describe("createSpinner", () => {
  it("defaults to the md size and the Loading label", () => {
    expect(createSpinner({})).toBe(
      '<span class="spinner spinner--md" role="status" aria-label="Loading"></span>',
    );
  });

  it("respects an explicit size", () => {
    expect(createSpinner({ size: "lg" })).toBe(
      '<span class="spinner spinner--lg" role="status" aria-label="Loading"></span>',
    );
  });

  it("respects an explicit label", () => {
    expect(createSpinner({ label: "Saving report" })).toBe(
      '<span class="spinner spinner--md" role="status" aria-label="Saving report"></span>',
    );
  });
});