import { useEffect, useState } from "react";
import { api, type Stats } from "../lib/api";
import { ci, ms, pct } from "../lib/format";

type Props = {
  refreshKey?: number;
};

export default function Scoreboard({ refreshKey = 0 }: Props) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    void api
      .stats("mdg-v1")
      .then((result) => {
        if (active) {
          setError("");
          setStats(result);
        }
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : "Scoreboard unavailable.");
      });
    return () => {
      active = false;
    };
  }, [refreshKey]);

  return (
    <section className="rounded-2xl border border-line bg-surface p-5" aria-labelledby="scoreboard-heading">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <div>
          <p className="font-mono text-xs tracking-[0.18em] text-accent">EVIDENCE</p>
          <h2 id="scoreboard-heading" className="mt-1 text-2xl font-semibold">
            Scoreboard
          </h2>
        </div>
        <p className="text-xs text-muted">Exact observed counts · 95% Wilson intervals</p>
      </div>
      {error && <p className="mt-4 text-sm text-muted">{error}</p>}
      {!error && !stats && <p className="mt-4 text-sm text-muted">Loading observed runs…</p>}
      {stats && stats.cohorts.length === 0 && <p className="mt-4 text-sm text-muted">No completed runs yet.</p>}
      {stats && stats.cohorts.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[680px] text-left text-sm">
            <caption className="sr-only">Observed motion puzzle results by cohort</caption>
            <thead className="border-b border-line text-xs uppercase tracking-wider text-muted">
              <tr>
                <th className="px-2 py-3 font-medium" scope="col">
                  Cohort
                </th>
                <th className="px-2 py-3 font-medium" scope="col">
                  N
                </th>
                <th className="px-2 py-3 font-medium" scope="col">
                  Passes
                </th>
                <th className="px-2 py-3 font-medium" scope="col">
                  Pass rate
                </th>
                <th className="px-2 py-3 font-medium" scope="col">
                  Round accuracy
                </th>
                <th className="px-2 py-3 font-medium" scope="col">
                  Mean time
                </th>
              </tr>
            </thead>
            <tbody>
              {stats.cohorts.map((cohort) => (
                <tr key={cohort.cohort} className="border-b border-line/60 last:border-0">
                  <th className="px-2 py-3 font-mono font-normal text-ink" scope="row">
                    {cohort.cohort}
                  </th>
                  <td className="px-2 py-3 font-mono">{cohort.attempts}</td>
                  <td className="px-2 py-3 font-mono">
                    {cohort.passes}/{cohort.attempts}
                  </td>
                  <td className="px-2 py-3">
                    <span className="font-mono">{pct(cohort.passRate)}</span>{" "}
                    <span className="text-xs text-muted">{ci(cohort.passCi)}</span>
                  </td>
                  <td className="px-2 py-3">
                    <span className="font-mono">{pct(cohort.roundAccuracy)}</span>{" "}
                    <span className="text-xs text-muted">{ci(cohort.roundCi)}</span>
                  </td>
                  <td className="px-2 py-3 font-mono">{ms(cohort.meanMs)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {stats.chance && (
            <p className="mt-3 text-xs text-muted">
              Chance: <span className="font-mono">{pct(stats.chance.round)}</span> per round ·{" "}
              <span className="font-mono">{pct(stats.chance.pass)}</span> for all three.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
