import { describe, expect, it } from "vitest";
import { reasonMessage } from "./reasons";

describe("physical failure copy", () => {
  it("prioritizes target guidance", () => {
    expect(reasonMessage(["gravity", "targets"])).toContain("three rings");
  });

  it("explains sensor consistency failures without blaming the user", () => {
    expect(reasonMessage(["gyro"])).toContain("sensors");
  });
});
