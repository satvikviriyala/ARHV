import { useEffect, useRef, useState } from "react";
import {
  ImuRecorder,
  requestMotionPermission,
  TargetTracker,
  type ImuChallenge,
  type ImuTrace,
  type TrackerState,
} from "../lib/imu";

// Phone-tilt challenge (imu-v1). "Marble on a plate": tilt right -> dot moves right; tilt the top of the phone
// toward you -> dot moves down. The dot must rest inside each ring until the ring fills.
const SCALE = 4.2; // px per degree of tilt
const SIZE = 300; // px, square play area
const SENSOR_STARTUP_GRACE_MS = 3000; // iOS/Android may deliver orientation after motion permission resolves

type Props = {
  challenge: ImuChallenge;
  onDone: (trace: ImuTrace) => void;
  onUnsupported?: () => void;
  autoFocus?: boolean;
};

type Status = "intro" | "denied" | "no-sensors" | "running" | "timeout";

export default function TiltChallenge({ challenge, onDone, onUnsupported, autoFocus = true }: Props) {
  const [status, setStatus] = useState<Status>("intro");
  const [state, setState] = useState<TrackerState | null>(null);
  const recorder = useRef<ImuRecorder | null>(null);
  const startButton = useRef<HTMLButtonElement>(null);

  useEffect(() => () => recorder.current?.stop(), []);
  useEffect(() => {
    if (autoFocus && (status === "intro" || status === "denied")) startButton.current?.focus();
  }, [autoFocus, status]);

  async function start() {
    const permission = await requestMotionPermission(); // runs inside the tap handler (iOS requirement)
    if (permission !== "granted") {
      setStatus(permission === "unsupported" ? "no-sensors" : "denied");
      if (permission === "unsupported") onUnsupported?.();
      return;
    }
    const rec = new ImuRecorder();
    const tracker = new TargetTracker(challenge);
    recorder.current = rec;
    rec.start();
    setStatus("running");
    let lastBuzz = 0;
    const tick = () => {
      if (!recorder.current) return;
      const t = rec.elapsedMs();
      if (t > SENSOR_STARTUP_GRACE_MS && !rec.hasMotion()) {
        rec.stop();
        setStatus("no-sensors");
        onUnsupported?.();
        return;
      }
      if (t > challenge.maxDurationMs) {
        rec.stop();
        setStatus("timeout");
        return;
      }
      const o = rec.latest();
      if (o) {
        const s = tracker.update(t, o.beta, o.gamma);
        setState(s);
        if (s.index > lastBuzz) {
          lastBuzz = s.index;
          navigator.vibrate?.(25); // Android haptic tick; ignored on iOS
        }
        if (s.phase === "done") {
          rec.stop();
          window.setTimeout(() => onDone(rec.trace(challenge)), 150); // a few extra samples after the last hold
          return;
        }
      }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  if (status === "intro" || status === "denied" || status === "no-sensors" || status === "timeout") {
    const msg = {
      intro: "Tilt your phone gently, screen up, to roll the dot into each ring. Keep each ring filled until it completes.",
      denied: "Motion access was blocked. Allow motion & orientation access for this site, then try again.",
      "no-sensors": "This device has no motion sensors. Open this page on your phone.",
      timeout: "Time's up. Try again with a fresh challenge.",
    }[status];
    return (
      <div className="flex flex-col items-center gap-4 text-center">
        <p className="max-w-sm text-muted">{msg}</p>
        {(status === "intro" || status === "denied") && (
          <button
            ref={startButton}
            type="button"
            onClick={start}
            className="rounded-xl bg-accent px-6 py-3 font-semibold text-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            {status === "denied" ? "Enable motion sensors and retry" : "Start physical check"}
          </button>
        )}
        {status === "denied" && (
          <button
            type="button"
            onClick={onUnsupported}
            className="text-sm text-muted underline decoration-accent underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Use the moving-shape alternative
          </button>
        )}
      </div>
    );
  }

  const target = state && state.phase !== "done" ? challenge.targets[state.index] : undefined;
  const dot = state?.offset ?? { dBeta: 0, dGamma: 0 };
  const px = (deg: number) => Math.max(-SIZE / 2 + 10, Math.min(SIZE / 2 - 10, deg * SCALE));
  const label =
    state?.phase === "baseline"
      ? "Hold still…"
      : state?.phase === "done"
        ? "Verified motion ✓"
        : `Ring ${Math.min((state?.index ?? 0) + 1, challenge.targets.length)} of ${challenge.targets.length}`;

  return (
    <div className="flex flex-col items-center gap-4" aria-live="polite">
      <p className="font-medium">{label}</p>
      <svg width={SIZE} height={SIZE} viewBox={`${-SIZE / 2} ${-SIZE / 2} ${SIZE} ${SIZE}`} role="img"
        aria-label="Tilt your phone to move the dot into the ring">
        <circle r={SIZE / 2 - 2} className="fill-surface stroke-line" strokeWidth={2} />
        <line x1={-8} x2={8} y1={0} y2={0} className="stroke-line" />
        <line x1={0} x2={0} y1={-8} y2={8} className="stroke-line" />
        {target && (
          <g transform={`translate(${px(target.dGamma)} ${px(target.dBeta)})`}>
            <circle r={target.radius * SCALE} className="fill-none stroke-accent" strokeWidth={3} />
            <circle
              r={target.radius * SCALE}
              className="fill-none stroke-ok"
              strokeWidth={5}
              pathLength={1}
              strokeDasharray={`${state?.holdProgress ?? 0} 1`}
              transform="rotate(-90)"
            />
          </g>
        )}
        <circle cx={px(dot.dGamma)} cy={px(dot.dBeta)} r={11} className="fill-ink" />
      </svg>
      <p className="max-w-sm text-center text-sm text-muted">About 10 seconds. Your phone&apos;s motion sensors are checked for physical consistency.</p>
    </div>
  );
}
