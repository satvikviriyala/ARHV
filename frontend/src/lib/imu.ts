// imu-v1 client: motion-permission flow, sensor capture and target tracking for the phone-tilt challenge.
// Mirrors backend/layers/core/pact_core/imu.py. The server re-verifies everything from the raw trace; the
// tracker here only drives the UI. Sample layout (keep in sync with the server):
// [t_ms, beta, gamma, alpha|null, gx, gy, gz, rAlpha, rBeta, rGamma]

export type ImuTarget = { dBeta: number; dGamma: number; radius: number; holdMs: number };
export type ImuChallenge = {
  challengeId: string;
  family: "imu-v1";
  nonce: string;
  targets: ImuTarget[];
  baselineMs: number;
  maxDurationMs: number;
  sampleHz: number;
  expiresAt?: number;
};
export type ImuSample = [number, number, number, number | null, number, number, number, number, number, number];
export type ImuTrace = { challengeId: string; nonce: string; samples: ImuSample[] };
export type MotionPermission = "granted" | "denied" | "unsupported";

const r1 = (x: number | null | undefined): number => Math.round((x ?? 0) * 10) / 10;

type PermissionApi = { requestPermission?: () => Promise<"granted" | "denied"> };

/** Must be called from a user gesture (tap). iOS 13+ needs BOTH motion and orientation permission. */
export async function requestMotionPermission(): Promise<MotionPermission> {
  if (typeof window === "undefined" || !("DeviceMotionEvent" in window) || !("DeviceOrientationEvent" in window)) {
    return "unsupported";
  }
  const motion = window.DeviceMotionEvent as unknown as PermissionApi;
  const orient = window.DeviceOrientationEvent as unknown as PermissionApi;
  try {
    const results = await Promise.all([
      motion.requestPermission ? motion.requestPermission() : Promise.resolve("granted" as const),
      orient.requestPermission ? orient.requestPermission() : Promise.resolve("granted" as const),
    ]);
    return results.every((r) => r === "granted") ? "granted" : "denied";
  } catch {
    return "denied"; // thrown when not called from a user gesture, or blocked by the browser
  }
}

/** Records merged orientation + motion samples. One sample per devicemotion event (~60 Hz). */
export class ImuRecorder {
  private readonly data: ImuSample[] = [];
  private t0 = 0;
  private orientation: { alpha: number | null; beta: number; gamma: number } | null = null;
  private running = false;
  private motionEvents = 0;

  private readonly onOrientation = (e: DeviceOrientationEvent) => {
    if (e.beta === null || e.gamma === null) return;
    this.orientation = { alpha: e.alpha, beta: e.beta, gamma: e.gamma };
  };

  private readonly onMotion = (e: DeviceMotionEvent) => {
    this.motionEvents += 1;
    if (!this.running || !this.orientation) return;
    const g = e.accelerationIncludingGravity;
    const r = e.rotationRate;
    if (!g || g.x === null || g.y === null || g.z === null) return;
    const o = this.orientation;
    this.data.push([
      Math.round((performance.now() - this.t0) * 10) / 10,
      r1(o.beta),
      r1(o.gamma),
      o.alpha === null ? null : r1(o.alpha),
      r1(g.x),
      r1(g.y),
      r1(g.z),
      r1(r?.alpha),
      r1(r?.beta),
      r1(r?.gamma),
    ]);
  };

  start(): void {
    this.data.length = 0;
    this.t0 = performance.now();
    this.running = true;
    window.addEventListener("deviceorientation", this.onOrientation);
    window.addEventListener("devicemotion", this.onMotion);
  }

  stop(): void {
    this.running = false;
    window.removeEventListener("deviceorientation", this.onOrientation);
    window.removeEventListener("devicemotion", this.onMotion);
  }

  /** Current (beta, gamma) for the UI, or null before the first orientation event. */
  latest(): { beta: number; gamma: number } | null {
    return this.orientation ? { beta: this.orientation.beta, gamma: this.orientation.gamma } : null;
  }

  elapsedMs(): number {
    return performance.now() - this.t0;
  }

  /** True once motion events arrive; false after ~1.5 s means sensors are unavailable (desktop, blocked). */
  hasMotion(): boolean {
    return this.motionEvents > 0;
  }

  trace(challenge: ImuChallenge): ImuTrace {
    return { challengeId: challenge.challengeId, nonce: challenge.nonce, samples: this.data.slice(0, 4000) };
  }
}

export const angDiff = (a: number, b: number): number => ((((a - b + 180) % 360) + 360) % 360) - 180;

export type TrackerState = {
  phase: "baseline" | "target" | "done";
  index: number; // current target index
  holdProgress: number; // 0..1 for the current target
  offset: { dBeta: number; dGamma: number }; // tilt relative to the user's own baseline
};

/** Same rules as the server (baseline median, targets in order, hold inside radius), minus the server's slack,
 * so "done" on the client implies the server's target check passes. */
export class TargetTracker {
  private readonly baseline: { b: number[]; g: number[] } = { b: [], g: [] };
  private b0: number | null = null;
  private g0 = 0;
  private index = 0;
  private holdStart: number | null = null;

  constructor(private readonly challenge: Pick<ImuChallenge, "targets" | "baselineMs">) {}

  update(tMs: number, beta: number, gamma: number): TrackerState {
    if (this.b0 === null) {
      this.baseline.b.push(beta);
      this.baseline.g.push(gamma);
      if (tMs < this.challenge.baselineMs) {
        return { phase: "baseline", index: 0, holdProgress: tMs / this.challenge.baselineMs, offset: { dBeta: 0, dGamma: 0 } };
      }
      const med = (xs: number[]) => [...xs].sort((a, c) => a - c)[Math.floor(xs.length / 2)] ?? 0;
      this.b0 = med(this.baseline.b);
      this.g0 = med(this.baseline.g);
    }
    const offset = { dBeta: angDiff(beta, this.b0), dGamma: angDiff(gamma, this.g0) };
    const target = this.challenge.targets[this.index];
    if (!target) return { phase: "done", index: this.index, holdProgress: 1, offset };
    const dist = Math.hypot(offset.dBeta - target.dBeta, offset.dGamma - target.dGamma);
    let holdProgress = 0;
    if (dist <= target.radius) {
      this.holdStart ??= tMs;
      holdProgress = Math.min(1, (tMs - this.holdStart) / target.holdMs);
      if (holdProgress >= 1) {
        this.index += 1;
        this.holdStart = null;
        if (this.index >= this.challenge.targets.length) return { phase: "done", index: this.index, holdProgress: 1, offset };
        return { phase: "target", index: this.index, holdProgress: 0, offset };
      }
    } else {
      this.holdStart = null;
    }
    return { phase: "target", index: this.index, holdProgress, offset };
  }

  baselineBeta(): number | null {
    return this.b0;
  }
}
