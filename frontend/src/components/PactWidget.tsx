import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { api, ApiError, type MdgChallenge } from "../lib/api";
import MdgCanvas from "./MdgCanvas";
import ShapeOptions from "./ShapeOptions";

type Props = {
  cohort?: string;
  onVerified: (token: string, details?: { assurance: "motion" }) => void;
};

type Status = "loading" | "round" | "submitting" | "passed" | "failed" | "error";

export default function PactWidget({ cohort = "public", onVerified }: Props) {
  const [status, setStatus] = useState<Status>("loading");
  const [challenge, setChallenge] = useState<MdgChallenge | null>(null);
  const [round, setRound] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [timings, setTimings] = useState<number[]>([]);
  const [correct, setCorrect] = useState(0);
  const [message, setMessage] = useState("");
  const firstFrame = useRef<number | null>(null);
  const retryButton = useRef<HTMLButtonElement>(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setMessage("");
    setChallenge(null);
    setRound(0);
    setAnswers([]);
    setTimings([]);
    firstFrame.current = null;
    try {
      const result = await api.createChallenge({ cohort });
      if (result.family !== "mdg-v1") throw new Error("The motion puzzle response was not mdg-v1.");
      setChallenge(result);
      setStatus("round");
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Could not start a puzzle.");
    }
  }, [cohort]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);
  useEffect(() => {
    if (status === "failed") retryButton.current?.focus();
  }, [status]);

  async function choose(answer: string) {
    if (!challenge || status !== "round") return;
    const nextAnswers = [...answers, answer];
    const nextTimings = [...timings, Math.max(0, Math.round(performance.now() - (firstFrame.current ?? performance.now())))];
    if (round < challenge.rounds.length - 1) {
      setAnswers(nextAnswers);
      setTimings(nextTimings);
      setRound(round + 1);
      firstFrame.current = null;
      return;
    }
    setAnswers(nextAnswers);
    setTimings(nextTimings);
    setStatus("submitting");
    try {
      const result = await api.submitAnswers(challenge.challengeId, nextAnswers, nextTimings, cohort);
      if (result.passed && result.token) {
        setStatus("passed");
        onVerified(result.token, { assurance: "motion" });
      } else {
        setCorrect(result.roundsCorrect ?? 0);
        setStatus("failed");
      }
    } catch (error) {
      setStatus("error");
      setMessage(
        error instanceof ApiError && (error.status === 409 || error.status === 410)
          ? "This check expired. Start a new one."
          : error instanceof Error
            ? error.message
            : "Could not submit the puzzle.",
      );
    }
  }

  if (status === "loading") {
    return <div className="h-[420px] w-full rounded-2xl bg-surface-2 motion-safe:animate-pulse" aria-label="Loading puzzle" />;
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
          Get a new puzzle
        </button>
      </div>
    );
  }
  if (status === "failed") {
    return (
      <div className="flex flex-col items-center gap-4 rounded-2xl border border-bad bg-bad/5 p-5 text-center" role="alert">
        <p className="font-mono text-xs tracking-[0.18em] text-bad">VERIFICATION REQUIRED</p>
        <p className="text-lg font-semibold text-bad">Suspicious activity detected. Please try human verification again.</p>
        <p className="text-sm text-muted">The motion puzzle result was not enough to confirm a person ({correct}/3 rounds).</p>
        <button
          ref={retryButton}
          type="button"
          onClick={() => void load()}
          className="rounded-xl bg-accent px-5 py-3 font-semibold text-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Try verification again
        </button>
        <Link
          to="/account"
          className="text-sm text-muted underline decoration-accent underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Can&apos;t use this? Verify with your account instead.
        </Link>
      </div>
    );
  }
  if (status === "passed") {
    return (
      <div className="rounded-2xl border border-ok p-5 text-center text-ok" aria-live="polite">
        Verified human · token valid for 2:00
      </div>
    );
  }
  if (!challenge) return null;
  const current = challenge.rounds[round]!;
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="w-full text-center" aria-live="polite">
        {status === "submitting" ? "Checking your answers…" : `Round ${round + 1} of ${challenge.rounds.length}`}
      </div>
      <MdgCanvas
        round={current}
        fps={challenge.fps}
        dot={challenge.dot}
        width={challenge.width}
        height={challenge.height}
        onFirstFrame={() => {
          firstFrame.current = performance.now();
        }}
      />
      {status === "round" && <ShapeOptions options={current.options} onSelect={(option) => void choose(option)} autoFocus />}
    </div>
  );
}
