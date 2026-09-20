import { useEffect, useMemo, useState } from "react";
import { api, getApiLog } from "../lib/api";
import { decodePayload, type TokenClaims } from "../lib/jwt";

type Props = {
  token?: string;
  metrics?: Record<string, unknown>;
  booked?: boolean;
};

export default function DevPanel({ token, metrics, booked = false }: Props) {
  const [open, setOpen] = useState(false);
  const claims = useMemo<TokenClaims>(() => (token ? decodePayload(token) : {}), [token]);
  const [explain, setExplain] = useState<{ decision?: string; policies?: string[] } | null>(null);
  const [calls, setCalls] = useState(getApiLog());

  useEffect(() => {
    if (!token) return;
    if (booked) {
      void api.explain(token).then(setExplain).catch(() => setExplain({ decision: "unavailable" }));
    }
    const timer = window.setInterval(() => setCalls(getApiLog()), 500);
    return () => window.clearInterval(timer);
  }, [booked, token]);

  return (
    <section className="rounded-2xl border border-line bg-surface">
      <button type="button" onClick={() => setOpen((value) => !value)} className="w-full p-4 text-left font-mono text-sm text-accent">
        {open ? "Hide" : "Show"} what AWS decided
      </button>
      {open && (
        <div className="space-y-3 border-t border-line p-4 text-xs">
          <p className="text-muted">Decoded token claims (display only; the browser does not verify them)</p>
          <pre className="overflow-auto rounded-lg bg-bg p-3 font-mono">{JSON.stringify(claims, null, 2)}</pre>
          {metrics && Object.keys(metrics).length > 0 && (
            <>
              <p className="text-muted">IMU verifier metrics</p>
              <pre className="overflow-auto rounded-lg bg-bg p-3 font-mono">{JSON.stringify(metrics, null, 2)}</pre>
            </>
          )}
          {explain && (
            <p className={explain.decision === "DENY" ? "text-ok" : "text-accent"}>
              {explain.decision} · {explain.policies?.join(", ") ?? "default-deny"}
            </p>
          )}
          <div>
            <p className="mb-1 text-muted">Recent API calls</p>
            <ul className="space-y-1 font-mono">
              {calls.slice(-5).map((call, index) => (
                <li key={`${call.path}-${index}`}>
                  {call.method} {call.path} · {call.status} · {call.ms}ms
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </section>
  );
}
