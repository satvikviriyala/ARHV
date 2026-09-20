import { useCallback, useEffect, useState } from "react";
import { api, type Booking } from "../lib/api";
import { getCohort } from "../lib/cohort";
import { ci, pct } from "../lib/format";
import BookingCard from "../components/BookingCard";
import DevPanel from "../components/DevPanel";
import PactWidget from "../components/PactWidget";
import PhysicalWidget from "../components/PhysicalWidget";
import VerifyChooser from "../components/VerifyChooser";

type Family = "imu-v1" | "mdg-v1";

export default function Home() {
  const cohort = getCohort();
  const [open, setOpen] = useState(false);
  const [family, setFamily] = useState<Family | null>(null);
  const [token, setToken] = useState("");
  const [metrics, setMetrics] = useState<Record<string, unknown>>({});
  const [booked, setBooked] = useState<Booking | null>(null);
  const [scoreboard, setScoreboard] = useState<{ attempts: number; passes: number; passCi: [number, number] } | null>(null);

  useEffect(() => {
    void api
      .stats("mdg-v1")
      .then((result) => {
        const study = result.cohorts.find((item) => item.cohort === "study");
        if (study && study.attempts > 0) setScoreboard(study);
      })
      .catch(() => setScoreboard(null));
  }, []);

  const onBooked = useCallback((result: Booking) => setBooked(result), []);
  const verified = useCallback((newToken: string, details?: { assurance?: "motion" | "physical"; metrics?: Record<string, unknown> }) => {
    setToken(newToken);
    setMetrics(details?.metrics ?? {});
    setOpen(false);
  }, []);

  function openChooser() {
    setFamily(null);
    setOpen(true);
  }

  return (
    <div className="space-y-10">
      <section className="grid gap-8 py-8 md:grid-cols-[1.15fr_0.85fr] md:items-center">
        <div>
          <p className="font-mono text-sm tracking-widest text-accent">ARHV · AGENT-RESISTANT HUMAN VERIFICATION</p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight md:text-6xl">Agents can read any screen. They can't tilt your phone.</h1>
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted">
            ARHV checks that a person physically moved a real device, just now, for this request. Screen puzzles are a race AI agents are winning; physical proof is where verification has to go.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <button type="button" onClick={openChooser} className="rounded-xl bg-accent px-5 py-3 font-semibold text-bg">
              Try it on your phone
            </button>
            <button type="button" onClick={openChooser} className="rounded-xl border border-line px-5 py-3">
              Book the last seat
            </button>
          </div>
        </div>
        <div className="rounded-2xl border border-line bg-surface p-6">
          <p className="text-sm text-muted">Fictional demo · 10:00:00 IST</p>
          <h2 className="mt-3 text-2xl font-semibold">Rush Hour Counter</h2>
          <p className="mt-2 text-accent">Tatkal-style rush · 1 seat left</p>
          <p className="mt-6 text-sm text-muted">A protected action sits behind API Gateway, Lambda, and a Cedar decision.</p>
          <button type="button" onClick={openChooser} className="mt-6 w-full rounded-xl bg-accent px-5 py-3 font-semibold text-bg">
            Book the last seat
          </button>
        </div>
      </section>

      {token && (
        <section className="space-y-4">
          <BookingCard token={token} onBooked={onBooked} />
          <DevPanel token={token} metrics={metrics} booked={Boolean(booked)} />
        </section>
      )}

      {scoreboard && (
        <section className="rounded-2xl border border-line bg-surface p-5">
          <p className="text-sm uppercase tracking-wider text-muted">Scoreboard · exact observed counts</p>
          <p className="mt-2">
            Humans (study): <span className="font-mono text-ok">{scoreboard.passes}/{scoreboard.attempts}</span> · pass rate{" "}
            <span className="font-mono">{pct(scoreboard.passes / scoreboard.attempts)}</span> · 95% CI {ci(scoreboard.passCi)}
          </p>
        </section>
      )}

      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-line p-5">
          <p className="font-mono text-accent">T0 · perceptual</p>
          <h3 className="mt-2 text-xl font-semibold">Motion puzzle</h3>
          <p className="mt-2 text-sm text-muted">A shape hides in moving dots. A screenshot is uniform noise.</p>
        </div>
        <div className="rounded-2xl border border-accent p-5">
          <p className="font-mono text-accent">T1 · physical</p>
          <h3 className="mt-2 text-xl font-semibold">Phone tilt</h3>
          <p className="mt-2 text-sm text-muted">Built today, unattested honestly: a physics-aware simulator can still pass.</p>
        </div>
        <div className="rounded-2xl border border-line p-5">
          <p className="font-mono text-accent">T2 · proposal</p>
          <h3 className="mt-2 text-xl font-semibold">Vendor-attested</h3>
          <p className="mt-2 text-sm text-muted">OS-signed gesture proofs and private, unlinkable tokens are the endgame.</p>
        </div>
      </section>

      {open && (
        <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/70 p-4" role="dialog" aria-modal="true" aria-labelledby="verify-title">
          <div className="max-h-[90dvh] w-full max-w-lg overflow-auto rounded-2xl border border-line bg-surface p-6 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-mono text-sm text-accent">RUSH HOUR COUNTER</p>
                <h2 id="verify-title" className="mt-1 text-2xl font-semibold">
                  Verify before booking
                </h2>
              </div>
              <button type="button" onClick={() => { setOpen(false); setFamily(null); }} aria-label="Close verification" className="text-2xl text-muted">
                ×
              </button>
            </div>
            <div className="mt-6">
              {!family && <VerifyChooser onChoose={(choice) => setFamily(choice)} />}
              {family === "imu-v1" && <PhysicalWidget cohort={cohort} onVerified={verified} onFallback={() => setFamily("mdg-v1")} />}
              {family === "mdg-v1" && <PactWidget cohort={cohort} onVerified={verified} />}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
