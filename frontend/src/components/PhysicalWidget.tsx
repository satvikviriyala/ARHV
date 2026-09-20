import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { api, ApiError } from "../lib/api";
import type { ImuChallenge, ImuTrace } from "../lib/imu";
import { reasonMessage } from "../lib/reasons";
import TiltChallenge from "./TiltChallenge";

type Props = {
  cohort?: string;
  onVerified: (token: string, details?: { assurance: "physical"; metrics?: Record<string, unknown> }) => void;
  onFallback?: () => void;
  sensorOnly?: boolean;
};

type Status = "loading" | "tilt" | "submitting" | "passed" | "failed" | "fallback" | "error";

export default function PhysicalWidget({ cohort = "public", onVerified, onFallback, sensorOnly = false }: Props) {
  const [status, setStatus] = useState<Status>("loading");
  const [challenge, setChallenge] = useState<ImuChallenge | null>(null);
  const [reasons, setReasons] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<Record<string, unknown>>({});
  const [message, setMessage] = useState("");
  const retryButton = useRef<HTMLButtonElement>(null);
  const attempt = useRef(0);
  const activeChallenge = useRef<string | null>(null);
  const submitting = useRef(false);
  const verified = useRef(false);

  const load = useCallback(async () => {
    const currentAttempt = ++attempt.current;
    submitting.current = false;
    verified.current = false;
    activeChallenge.current = null;
    setStatus("loading");
    setChallenge(null);
    setReasons([]);
    setMessage("");
    try {
      const result = await api.createChallenge({ family: "imu-v1", cohort });
      if (currentAttempt !== attempt.current) return;
      if (result.family !== "imu-v1") throw new Error("The physical challenge response was not imu-v1.");
      activeChallenge.current = result.challengeId;
      setChallenge(result);
      setStatus("tilt");
    } catch (error) {
      if (currentAttempt !== attempt.current) return;
      setMessage(error instanceof Error ? error.message : "Could not start the physical check.");
      setStatus("error");
    }
  }, [cohort]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);
  useEffect(() => {
    if (status === "failed") retryButton.current?.focus();
  }, [status]);

  async function submit(trace: ImuTrace) {
    const challengeId = activeChallenge.current;
    if (verified.current || submitting.current || challengeId !== trace.challengeId) return;
    submitting.current = true;
    setStatus("submitting");
    try {
      const result = await api.submitTrace(trace.challengeId, trace, cohort);
      if (challengeId !== activeChallenge.current) return;
      setMetrics(result.metrics ?? {});
      if (result.passed && result.token) {
        verified.current = true;
        setStatus("passed");
        onVerified(result.token, { assurance: "physical", metrics: result.metrics });
      } else {
        submitting.current = false;
        setReasons(result.reasons ?? []);
        setStatus("failed");
      }
    } catch (error) {
      if (challengeId !== activeChallenge.current) return;
      submitting.current = false;
      setMessage(
        error instanceof ApiError && (error.status === 409 || error.status === 410)
          ? "This check expired. Start a new one."
          : error instanceof Error
            ? error.message
            : "Could not submit the physical check.",
      );
      setStatus("error");
    }
  }

  if (status === "loading") {
    return <div className="h-[420px] w-full rounded-2xl bg-surface-2 motion-safe:animate-pulse" aria-label="Loading physical check" />;
  }
  if (status === "error") {
    return (
      <div className="flex flex-col items-center gap-4 text-center">
        <p className="text-bad">{message}</p>
        <button
          type="button"
          onClick={() => void load()}
          className="rounded-xl bg-accent px-5 py-3 font-semibold text-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Try again
        </button>
      </div>
    );
  }
  if (status === "fallback") {
    return (
      <div className="flex flex-col items-center gap-4 rounded-2xl border border-line p-5 text-center">
        <p>Motion sensors aren&apos;t available here for this quick presence check.</p>
        <button
          type="button"
          onClick={onFallback}
          className="rounded-xl border border-accent px-5 py-3 text-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Spot the moving shape instead
        </button>
        <Link
          to="/account"
          className="text-sm text-muted underline decoration-accent underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Can&apos;t use motion? Verify with your account instead.
        </Link>
      </div>
    );
  }
  if (status === "failed") {
    return (
      <div className="flex flex-col items-center gap-4 rounded-2xl border border-bad bg-bad/5 p-5 text-center" role="alert">
        <p className="font-mono text-xs tracking-[0.18em] text-bad">VERIFICATION REQUIRED</p>
        <p className="text-lg font-semibold text-bad">Motion signal incomplete. Please try the sensors again.</p>
        <p className="text-sm text-muted">{reasonMessage(reasons)}</p>
        <button
          ref={retryButton}
          type="button"
          onClick={() => void load()}
          className="rounded-xl bg-accent px-5 py-3 font-semibold text-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Try sensors again
        </button>
        {!sensorOnly && (
          <Link
            to="/account"
            className="text-sm text-muted underline decoration-accent underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Can&apos;t use motion? Verify with your account instead.
          </Link>
        )}
        <p className="text-xs text-muted">Metrics are available in “Show what AWS decided”.</p>
      </div>
    );
  }
  if (status === "passed") {
    return <div className="rounded-2xl border border-ok p-5 text-center text-ok">Presence verified · physical proof · phone tilt</div>;
  }
  if (!challenge) return null;
  return (
    <div className="flex flex-col items-center gap-4">
      {status === "submitting" ? (
        <p aria-live="polite">Checking the sensor physics…</p>
      ) : (
        <TiltChallenge
          challenge={challenge}
          onDone={(trace) => void submit(trace)}
          onUnsupported={() => {
            if (onFallback) {
              setStatus("fallback");
            } else {
              setMessage("Motion sensors were not available. Check access and try the sensors again.");
              setStatus("error");
            }
          }}
          showAlternative={!sensorOnly && Boolean(onFallback)}
          autoFocus
        />
      )}
      <p className="max-w-sm text-center text-xs text-muted">The server checks gravity, orientation, timing, continuity, and gyro motion—not a client-side “done” flag.</p>
      {Object.keys(metrics).length > 0 && <span className="sr-only">{JSON.stringify(metrics)}</span>}
    </div>
  );
}
