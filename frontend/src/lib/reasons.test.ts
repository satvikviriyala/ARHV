import { describe, expect, it } from "vitest";
import { reasonMessage, verificationDisposition } from "./reasons";

describe("physical verification failure classification", () => {
  it("keeps ambiguous mobile readings on the retry path", () => {
    expect(verificationDisposition(["tilt"], { tiltErrDeg: 22 })).toBe("retry");
    expect(reasonMessage(["tilt"])).toContain("ambiguous");
  });

  it("marks structurally impossible sensor evidence as suspicious", () => {
    expect(verificationDisposition(["gravity", "tilt", "gyro"], { gravityFrac: 0, gyroCorr: [0, 0] })).toBe(
      "suspicious",
    );
    expect(verificationDisposition(["continuity"], { maxJumpDeg: 31 })).toBe("suspicious");
    expect(verificationDisposition(["gyro"], { gyroCorr: [0, 0] })).toBe("suspicious");
  });
});

describe("physical failure copy", () => {
  it("prioritizes target guidance", () => {
    expect(reasonMessage(["gravity", "targets"])).toContain("three rings");
  });

  it("explains sensor consistency failures without blaming the user", () => {
    expect(reasonMessage(["gyro"])).toContain("ambiguous");
  });
});
