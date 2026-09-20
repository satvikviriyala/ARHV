import { describe, expect, it, vi } from "vitest";
import { angDiff, ImuRecorder, TargetTracker } from "./imu";

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

describe("ImuRecorder", () => {
  it("only exposes complete motion-plus-orientation samples to the tracker", () => {
    const recorder = new ImuRecorder();
    const now = vi.spyOn(performance, "now");
    now.mockReturnValue(100);
    recorder.start();

    const orientation = new Event("deviceorientation");
    Object.defineProperties(orientation, {
      alpha: { value: 12.3 },
      beta: { value: 24.2 },
      gamma: { value: -8.4 },
    });
    window.dispatchEvent(orientation);

    expect(recorder.latest()).toEqual({ beta: 24.2, gamma: -8.4 });
    expect(recorder.latestComplete()).toBeNull();

    now.mockReturnValue(116.7);
    const motion = new Event("devicemotion");
    Object.defineProperties(motion, {
      accelerationIncludingGravity: { value: { x: 1, y: 2, z: 9.5 } },
      rotationRate: { value: { alpha: 0.1, beta: 0.2, gamma: 0.3 } },
    });
    window.dispatchEvent(motion);

    expect(recorder.latestComplete()).toEqual({ tMs: 16.7, beta: 24.2, gamma: -8.4 });
    recorder.stop();
    now.mockRestore();
  });
});

describe("angDiff", () => {
  it("wraps around 360", () => {
    expect(angDiff(179, -179)).toBe(-2);
    expect(angDiff(-179, 179)).toBe(2);
    expect(angDiff(10, 5)).toBe(5);
  });
});
