import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import type { ImuChallenge, ImuTrace } from "../lib/imu";
import { reasonMessage } from "../lib/reasons";
import TiltChallenge from "./TiltChallenge";

type Props = {
  cohort?: string;
  onVerified: (token: string, details?: { assurance: "physical"; metrics?: Record<string, unknown> }) => void;
  onFallback?: () => void;
};

type Status = "loading" | "tilt" | "submitting" | "passed" | "failed" | "fallback" | "error";

export default function PhysicalWidget({ cohort = "public", onVerified, onFallback }: Props) {
  const [status, setStatus] = useState<Status>("loading");
  const [challenge, setChallenge] = useState<ImuChallenge | null>(null);
  const [reasons, setReasons] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<Record<string, unknown>>({});
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setStatus("loading");
    setChallenge(null);
    setReasons([]);
    setMessage("");
    try {
      const result = await api.createChallenge({ family: "imu-v1", cohort });
      if (result.family !== "imu-v1") throw new Error("The physical challenge response was not imu-v1.");
      setChallenge(result);
      setStatus("tilt");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not start the physical check.");
      setStatus("error");
    }
  }, [cohort]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  async function submit(trace: ImuTrace) {
    setStatus("submitting");
    try {
      const result = await api.submitTrace(trace.challengeId, trace, cohort);
      setMetrics(result.metrics ?? {});
      if (result.passed && result.token) {
        setStatus("passed");
        onVerified(result.token, { assurance: "physical", metrics: result.metrics });
      } else {
        setReasons(result.reasons ?? []);
        setStatus("failed");
      }
    } catch (error) {
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
    return <div className="h-[420px] w-full animate-pulse rounded-2xl bg-surface-2" aria-label="Loading physical check" />;
  }
  if (status === "error") {
    return (
      <div className="flex flex-col items-center gap-4 text-center">
        <p className="text-bad">{message}</p>
        <button type="button" onClick={() => void load()} className="rounded-xl bg-accent px-5 py-3 font-semibold text-bg">
          Try again
        </button>
      </div>
    );
  }
  if (status === "fallback") {
    return (
      <div className="flex flex-col items-center gap-4 rounded-2xl border border-line p-5 text-center">
        <p>Motion sensors aren't available here.</p>
        <button type="button" onClick={onFallback} className="rounded-xl border border-accent px-5 py-3 text-accent">
          Spot the shape instead
        </button>
      </div>
    );
  }
  if (status === "failed") {
    return (
      <div className="flex flex-col items-center gap-4 text-center">
        <p className="text-bad">{reasonMessage(reasons)}</p>
        <button type="button" onClick={() => void load()} className="rounded-xl bg-accent px-5 py-3 font-semibold text-bg">
          Try again
        </button>
        <p className="text-xs text-muted">Metrics are available in “Show what AWS decided”.</p>
      </div>
    );
  }
  if (status === "passed") {
    return <div className="rounded-2xl border border-ok p-5 text-center text-ok">Verified · physical proof · phone tilt</div>;
  }
  if (!challenge) return null;
  return (
    <div className="flex flex-col items-center gap-4">
      {status === "submitting" ? (
        <p aria-live="polite">Checking the sensor physics…</p>
      ) : (
        <TiltChallenge challenge={challenge} onDone={(trace) => void submit(trace)} onUnsupported={() => setStatus("fallback")} />
      )}
      <p className="max-w-sm text-center text-xs text-muted">The server checks gravity, orientation, timing, continuity, and gyro motion.</p>
      {Object.keys(metrics).length > 0 && <span className="sr-only">{JSON.stringify(metrics)}</span>}
    </div>
  );
}
