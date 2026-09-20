import { describe, expect, it } from "vitest";
import { angDiff, TargetTracker } from "./imu";

const challenge = {
  baselineMs: 600,
  targets: [
    { dBeta: 20, dGamma: 0, radius: 8, holdMs: 450 },
    { dBeta: 0, dGamma: -20, radius: 8, holdMs: 450 },
  ],
};

describe("TargetTracker", () => {
  it("uses the user's own baseline, then requires each target held in order", () => {
    const tr = new TargetTracker(challenge);
    let t = 0;
    for (; t < 600; t += 16) expect(tr.update(t, 50, 3).phase).toBe("baseline");
    expect(tr.update(t, 50, 3).offset).toEqual({ dBeta: 0, dGamma: 0 });
    // leaving the target early resets the hold
    tr.update((t += 16), 70, 3);
    tr.update((t += 200), 70, 3);
    expect(tr.update((t += 16), 50, 3).holdProgress).toBe(0);
    // hold target 1 for 450 ms
    tr.update((t += 16), 69, 4);
    let s = tr.update((t += 460), 71, 2);
    expect(s.index).toBe(1);
    // target 2 is relative to the same baseline
    tr.update((t += 16), 50, -17);
    s = tr.update(t + 460, 51, -18);
    expect(s.phase).toBe("done");
  });

  it("uses the server's sensor-noise slack for mobile delivery jitter", () => {
    const tr = new TargetTracker({
      baselineMs: 600,
      targets: [{ dBeta: 20, dGamma: 0, radius: 8, holdMs: 450 }],
    });
    let t = 0;
    for (; t <= 600; t += 100) tr.update(t, 0, 0);
    tr.update((t += 100), 30, 0); // radius + 2 boundary
    const done = tr.update(t + 360, 30, 0); // 80% of the server hold
    expect(done.phase).toBe("done");
  });
});

describe("angDiff", () => {
  it("wraps around 360", () => {
    expect(angDiff(179, -179)).toBe(-2);
    expect(angDiff(-179, 179)).toBe(2);
    expect(angDiff(10, 5)).toBe(5);
  });
});
