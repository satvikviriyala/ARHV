import { useEffect, useState } from "react";
import { ApiError, api, type AgentRun, type Health } from "../lib/api";
import AgentRunView from "../components/AgentRunView";
import Scoreboard from "../components/Scoreboard";

type FrameCount = 1 | 4 | 8;

function modelLabel(alias: string): string {
  const labels: Record<string, string> = {
    "nova-2-lite": "Amazon Nova 2 Lite",
    "nova-pro": "Amazon Nova Pro",
    claude: "Claude on Amazon Bedrock",
  };
  return labels[alias] ?? alias;
}

export default function Lab() {
  const [health, setHealth] = useState<Health | null>(null);
  const [healthError, setHealthError] = useState("");
  const [model, setModel] = useState("");
  const [frames, setFrames] = useState<FrameCount>(4);
  const [runId, setRunId] = useState("");
  const [run, setRun] = useState<AgentRun | null>(null);
  const [replay, setReplay] = useState<AgentRun["replay"] | null>(null);
  const [message, setMessage] = useState("");
  const [starting, setStarting] = useState(false);
  const [scoreboardRefresh, setScoreboardRefresh] = useState(0);

  useEffect(() => {
    let active = true;
    void api
      .health()
      .then((result) => {
        if (!active) return;
        setHealth(result);
        setModel(result.agentModels[0] ?? "");
      })
      .catch((reason: unknown) => {
        if (active) setHealthError(reason instanceof Error ? reason.message : "Could not load the red-team service.");
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!runId) return;
    let active = true;
    let timer = 0;
    const startedAt = Date.now();

    const poll = async () => {
      try {
        const current = await api.getAgentRun(runId);
        if (!active) return;
        setRun(current);
        if (current.status === "done") {
          const completed = await api.getAgentRun(runId, { replay: true });
          if (active) {
            setRun(completed);
            setReplay(completed.replay ?? null);
            setScoreboardRefresh((value) => value + 1);
          }
          return;
        }
        if (current.status === "error") return;
        if (Date.now() - startedAt >= 120_000) {
          setMessage("Polling timed out. The worker may still finish; refresh the Lab to check.");
          return;
        }
        timer = window.setTimeout(() => void poll(), 1_500);
      } catch (reason: unknown) {
        if (active) setMessage(reason instanceof Error ? reason.message : "Could not poll the red-team run.");
      }
    };

    void poll();
    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [runId]);

  async function startRun() {
    if (!model || starting) return;
    setStarting(true);
    setMessage("");
    setRun(null);
    setReplay(null);
    try {
      const queued = await api.startAgentRun(model, frames);
      setRunId(queued.runId);
      setRun({
        runId: queued.runId,
        status: "queued",
        model,
        modelId: "",
        frames,
        progress: 0,
        createdAt: Math.floor(Date.now() / 1000),
        passed: false,
        roundsCorrect: 0,
        error: null,
        rounds: [],
      });
    } catch (reason: unknown) {
      const fallback =
        reason instanceof ApiError && reason.code === "cloud_only"
          ? "Cloud runs are disabled locally. Run `make bench BACKEND=ollama` for the local fallback."
          : reason instanceof Error
            ? reason.message
            : "Could not start the red-team run.";
      setMessage(fallback);
    } finally {
      setStarting(false);
    }
  }

  return (
    <div className="space-y-8">
      <section className="mx-auto max-w-4xl space-y-5">
        <p className="font-mono text-sm tracking-widest text-accent">RED-TEAM LAB</p>
        <h1 className="text-4xl font-semibold md:text-5xl">Watch an AI try the same puzzle.</h1>
        <p className="max-w-3xl text-lg leading-relaxed text-muted">
          ARHV gives a Strands vision agent the same motion-defined glyph challenge, with a generous K-frame
          window. The API queues the run; the worker calls Amazon Bedrock, stores the frames in S3, and scores the
          answers with the same server verifier.
        </p>
      </section>

      <section className="mx-auto max-w-4xl rounded-2xl border border-line bg-surface p-5" aria-labelledby="run-controls-heading">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <div>
            <p className="font-mono text-xs tracking-widest text-accent">ASYNC WORKER</p>
            <h2 id="run-controls-heading" className="mt-1 text-2xl font-semibold">
              Start a measured attack
            </h2>
          </div>
          <span className="text-xs text-muted">Daily cap enforced by DynamoDB</span>
        </div>
        {healthError && <p className="mt-4 text-sm text-bad">{healthError}</p>}
        {!health && !healthError && <p className="mt-4 text-sm text-muted">Loading available Bedrock models…</p>}
        {health && !health.cloudAgents && (
          <p className="mt-4 rounded-xl border border-accent p-4 text-sm text-muted">
            This is the local Build It path. Cloud worker runs are disabled here; run{" "}
            <code className="font-mono text-accent">make bench BACKEND=ollama</code> against the local API.
          </p>
        )}
        {health?.cloudAgents && (
          <form
            className="mt-5 grid gap-5 md:grid-cols-[1fr_auto_auto]"
            onSubmit={(event) => {
              event.preventDefault();
              void startRun();
            }}
          >
            <label className="flex flex-col gap-2 text-sm">
              <span className="text-muted">Model</span>
              <select
                value={model}
                onChange={(event) => setModel(event.target.value)}
                className="rounded-xl border border-line bg-bg px-3 py-3 text-ink focus-visible:outline-2 focus-visible:outline-accent"
                disabled={starting}
              >
                {health.agentModels.map((alias) => (
                  <option key={alias} value={alias}>
                    {modelLabel(alias)}
                  </option>
                ))}
              </select>
            </label>
            <fieldset>
              <legend className="text-sm text-muted">Frames per round</legend>
              <div className="mt-2 flex gap-2" role="group" aria-label="Frames per round">
                {([1, 4, 8] as const).map((count) => (
                  <button
                    key={count}
                    type="button"
                    aria-pressed={frames === count}
                    onClick={() => setFrames(count)}
                    className={`rounded-xl border px-4 py-3 font-mono focus-visible:outline-2 focus-visible:outline-accent ${
                      frames === count ? "border-accent text-accent" : "border-line text-muted"
                    }`}
                    disabled={starting}
                  >
                    {count}
                  </button>
                ))}
              </div>
            </fieldset>
            <button
              type="submit"
              disabled={starting || !model}
              className="self-end rounded-xl bg-accent px-5 py-3 font-semibold text-bg disabled:cursor-not-allowed disabled:opacity-50"
            >
              {starting ? "Queueing…" : "Let the AI try"}
            </button>
          </form>
        )}
        {message && (
          <p className="mt-4 rounded-xl border border-bad p-4 text-sm text-bad" role="alert">
            {message}
          </p>
        )}
      </section>

      {run && (
        <div className="mx-auto max-w-5xl">
          <AgentRunView run={run} replay={replay} />
        </div>
      )}

      <div className="mx-auto max-w-5xl">
        <Scoreboard refreshKey={scoreboardRefresh} />
      </div>
    </div>
  );
}
