import type { AgentRun, MdgChallenge } from "../lib/api";
import MdgCanvas from "./MdgCanvas";

type Props = {
  run: AgentRun;
  replay?: MdgChallenge | null;
};

export default function AgentRunView({ run, replay }: Props) {
  if (run.status === "error") {
    return (
      <section className="rounded-2xl border border-bad bg-bad/5 p-5" aria-live="polite">
        <p className="font-mono text-sm tracking-widest text-bad">INFRASTRUCTURE ERROR</p>
        <h2 className="mt-2 text-2xl font-semibold">This run was not scored as an agent failure.</h2>
        <p className="mt-2 text-sm text-muted">{run.error ?? "The worker stopped before producing a result."}</p>
      </section>
    );
  }

  if (run.status !== "done") {
    return (
      <section className="rounded-2xl border border-line bg-surface p-5" aria-live="polite">
        <p className="font-mono text-sm tracking-widest text-accent">WORKER STATUS</p>
        <h2 className="mt-2 text-2xl font-semibold">
          {run.status === "queued" ? "Queued for Amazon Bedrock…" : `Round ${run.progress + 1} of 3`}
        </h2>
        <p className="mt-2 text-sm text-muted">
          The API returned immediately. The worker is asking {run.model} asynchronously.
        </p>
      </section>
    );
  }

  return (
    <section className="space-y-5" aria-labelledby="agent-result-heading">
      <div className={`rounded-2xl border p-5 ${run.passed ? "border-accent bg-accent/5" : "border-bad bg-bad/5"}`}>
        <p className={`font-mono text-sm tracking-widest ${run.passed ? "text-accent" : "text-bad"}`}>VERDICT</p>
        <h2 id="agent-result-heading" className="mt-2 text-3xl font-semibold">
          {run.passed ? "AI PASSED" : `AI FAILED (${run.roundsCorrect}/3)`}
        </h2>
        <p className="mt-2 text-sm text-muted">
          Same challenge, same verifier. K={run.frames} consecutive frame{run.frames === 1 ? "" : "s"} per round.
        </p>
      </div>

      {run.rounds.map((round) => {
        const replayRound = replay?.rounds[round.index];
        return (
          <article key={round.index} className="rounded-2xl border border-line bg-surface p-5">
            <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="text-xl font-semibold">Round {round.index + 1}</h3>
              <span className="font-mono text-xs text-muted">{round.latencyMs ?? 0} ms model latency</span>
            </div>
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <p className="mb-3 font-mono text-xs tracking-widest text-accent">WHAT THE AI SAW</p>
                {round.frameUrls && round.frameUrls.length > 0 ? (
                  <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                    {round.frameUrls.map((url, index) => (
                      <a
                        key={url}
                        href={url}
                        target="_blank"
                        rel="noreferrer"
                        aria-label={`Open AI frame ${index + 1} for round ${round.index + 1}`}
                        className="rounded-lg border border-line bg-bg p-1 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
                      >
                        <img src={url} alt={`AI frame ${index + 1}`} className="aspect-square w-full rounded object-contain" />
                      </a>
                    ))}
                  </div>
                ) : (
                  <p className="rounded-xl border border-dashed border-line p-4 text-sm text-muted">Frame artifacts unavailable.</p>
                )}
              </div>
              <div>
                <p className="mb-3 font-mono text-xs tracking-widest text-accent">WHAT YOU SEE</p>
                {replayRound && replay ? (
                  <MdgCanvas
                    round={replayRound}
                    fps={replay.fps}
                    dot={replay.dot}
                    width={replay.width}
                    height={replay.height}
                  />
                ) : (
                  <p className="rounded-xl border border-dashed border-line p-4 text-sm text-muted">Replay is not available.</p>
                )}
              </div>
            </div>
            <dl className="mt-5 grid gap-3 border-t border-line pt-4 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-muted">AI answer</dt>
                <dd className="mt-1 font-mono">{round.answer || "invalid / no answer"}</dd>
              </div>
              <div>
                <dt className="text-muted">Confidence</dt>
                <dd className="mt-1 font-mono">
                  {typeof round.confidence === "number" ? round.confidence.toFixed(2) : "—"}
                </dd>
              </div>
              <div>
                <dt className="text-muted">Verifier result</dt>
                <dd className="mt-1 font-mono">
                  {round.correct ? "✓ correct" : "✗ wrong"}
                  {round.truth ? ` · expected ${round.truth}` : ""}
                </dd>
              </div>
              <div>
                <dt className="text-muted">Reply</dt>
                <dd className="mt-1">{round.repaired ? "Repaired once" : round.valid ? "Valid JSON" : "Invalid JSON"}</dd>
              </div>
            </dl>
            {round.rationale && <p className="mt-4 text-sm text-muted">Rationale: {round.rationale}</p>}
          </article>
        );
      })}
    </section>
  );
}
