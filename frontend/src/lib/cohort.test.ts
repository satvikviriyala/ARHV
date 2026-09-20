import { beforeEach, describe, expect, it } from "vitest";
import { getCohort } from "./cohort";

describe("cohort", () => {
  beforeEach(() => {
    sessionStorage.clear();
    window.history.pushState({}, "", "/");
  });

  it("persists a valid query cohort", () => {
    window.history.pushState({}, "", "/?cohort=study");
    expect(getCohort()).toBe("study");
    window.history.pushState({}, "", "/");
    expect(getCohort()).toBe("study");
  });

  it("sanitizes invalid cohorts to public", () => {
    window.history.pushState({}, "", "/?cohort=../../bad");
    expect(getCohort()).toBe("public");
  });
});
