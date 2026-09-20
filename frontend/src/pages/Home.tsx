import { useCallback, useEffect, useState } from "react";
import { ShieldCheck, TrainFront } from "lucide-react";
import { Link } from "react-router";
import { api, type Booking } from "../lib/api";
import { getCohort } from "../lib/cohort";
import { ci, pct } from "../lib/format";
import BookingCard from "../components/BookingCard";
import DevPanel from "../components/DevPanel";
import JourneySearch from "../components/JourneySearch";
import PactWidget from "../components/PactWidget";
import PhysicalWidget from "../components/PhysicalWidget";
import TrainResults from "../components/TrainResults";
import VerifyChooser from "../components/VerifyChooser";
import { DEFAULT_JOURNEY, formatJourneyDate, journeyLabel, type Journey, type TrainOption } from "../lib/rail";

type Family = "imu-v1" | "mdg-v1";

export default function Home() {
  const cohort = getCohort();
  const [journey, setJourney] = useState<Journey>(DEFAULT_JOURNEY);
  const [searched, setSearched] = useState(false);
  const [open, setOpen] = useState(false);
  const [family, setFamily] = useState<Family | null>(null);
  const [selectedTrain, setSelectedTrain] = useState<TrainOption | null>(null);
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
  const onSearch = useCallback(() => {
    setSearched(true);
    setSelectedTrain(null);
    setToken("");
    setBooked(null);
    const target = document.getElementById("journey-search");
    target?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }, []);
  const openVerification = useCallback((train: TrainOption) => {
    setSelectedTrain(train);
    setFamily(null);
    setOpen(true);
  }, []);
  const verified = useCallback(
    (newToken: string, details?: { assurance?: "motion" | "physical"; metrics?: Record<string, unknown> }) => {
      setToken(newToken);
      setMetrics(details?.metrics ?? {});
      setOpen(false);
      setFamily(null);
    },
    [],
  );

  return (
    <div className="space-y-12">
      <section className="grid gap-8 py-4 md:grid-cols-[1.1fr_0.9fr] md:items-center md:py-8">
        <div>
          <div className="flex flex-wrap items-center gap-2 text-xs font-semibold tracking-[0.16em] text-accent">
            <span>ARHV RAIL</span>
            <span className="rounded-full border border-accent/40 px-2 py-1 font-mono tracking-normal">FICTIONAL DEMO</span>
          </div>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight md:text-6xl">
            Reserve the route.
            <span className="block text-accent">Prove you&apos;re present.</span>
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted">
            Agents can read any screen. ARHV checks that a person physically moved a real phone, just now, for this journey.
            The result is a single-use token for the protected booking action.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              to="/phone"
              className="rounded-xl bg-accent px-5 py-3 font-semibold text-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              Try it on your phone
            </Link>
            <button
              type="button"
              onClick={onSearch}
              className="rounded-xl border border-line px-5 py-3 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              Find a journey
            </button>
          </div>
          <p className="mt-6 flex items-start gap-2 text-sm text-muted">
            <ShieldCheck size={18} className="mt-0.5 shrink-0 text-ok" aria-hidden="true" />
            Fresh route selection · server-checked presence · Cedar-protected booking
          </p>
        </div>

        <aside className="relative overflow-hidden rounded-3xl border border-line bg-surface p-6 sm:p-8">
          <div className="absolute -right-12 -top-12 size-40 rounded-full bg-accent/10 blur-3xl" aria-hidden="true" />
          <div className="relative">
            <div className="flex items-center justify-between gap-4">
              <p className="font-mono text-xs tracking-[0.18em] text-accent">NEXT RELEASE</p>
              <TrainFront size={24} className="text-accent" aria-hidden="true" />
            </div>
            <h2 className="mt-5 text-3xl font-semibold">Peak-hour journeys</h2>
            <p className="mt-2 text-sm leading-relaxed text-muted">A fictional rail counter for showing how physical presence can protect scarce digital actions.</p>
            <div className="mt-6 rounded-2xl border border-line bg-bg p-4">
              <p className="text-xs uppercase tracking-wider text-muted">Popular route</p>
              <p className="mt-2 text-lg font-medium">{journeyLabel(DEFAULT_JOURNEY)}</p>
              <p className="mt-1 text-sm text-muted">{formatJourneyDate(DEFAULT_JOURNEY.date)} · 12 seats open</p>
            </div>
            <div className="mt-6 flex items-center justify-between text-sm">
              <span className="text-muted">Release availability</span>
              <span className="font-mono text-accent">12 / 20</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-surface-2" aria-label="12 of 20 seats available">
              <div className="h-full w-3/5 rounded-full bg-accent" />
            </div>
          </div>
        </aside>
      </section>

      <section id="journey-search" className="scroll-mt-6 space-y-6" aria-labelledby="journey-heading">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs tracking-[0.18em] text-accent">ARHV RAIL COUNTER</p>
            <h2 id="journey-heading" className="mt-2 text-3xl font-semibold">
              Plan your journey
            </h2>
            <p className="mt-2 max-w-2xl text-muted">Choose a route, date, class, and quota. Then select a fictional service to continue.</p>
          </div>
          <span className="rounded-full border border-line px-3 py-1 text-xs text-muted">No real tickets are issued</span>
        </div>
        <JourneySearch journey={journey} onChange={setJourney} onSubmit={onSearch} />
        {searched ? (
          <TrainResults journey={journey} onBook={openVerification} />
        ) : (
          <div className="rounded-2xl border border-dashed border-line p-6 text-center text-sm text-muted">
            Search to see available services for {journeyLabel(journey)}.
          </div>
        )}
      </section>

      {token && selectedTrain && (
        <section className="space-y-4" aria-labelledby="booking-result-heading">
          <div>
            <p className="font-mono text-xs tracking-[0.18em] text-accent">PROTECTED ACTION</p>
            <h2 id="booking-result-heading" className="mt-2 text-2xl font-semibold">Your journey is ready</h2>
          </div>
          <BookingCard token={token} journey={journey} train={selectedTrain} onBooked={onBooked} />
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

      <section className="grid gap-4 md:grid-cols-3" aria-label="ARHV verification tiers">
        <div className="rounded-2xl border border-line p-5">
          <p className="font-mono text-accent">T0 · perceptual</p>
          <h3 className="mt-2 text-xl font-semibold">Spot the moving shape</h3>
          <p className="mt-2 text-sm text-muted">A shape hides in moving dots. A single screenshot is uniform noise.</p>
        </div>
        <div className="rounded-2xl border border-accent p-5">
          <p className="font-mono text-accent">T1 · physical</p>
          <h3 className="mt-2 text-xl font-semibold">Tilt your phone</h3>
          <p className="mt-2 text-sm text-muted">Gravity, orientation, gyro, timing, and fresh targets are checked server-side.</p>
        </div>
        <div className="rounded-2xl border border-line p-5">
          <p className="font-mono text-accent">T2 · proposal</p>
          <h3 className="mt-2 text-xl font-semibold">Vendor-attested</h3>
          <p className="mt-2 text-sm text-muted">OS-signed gesture proofs and private, unlinkable tokens are the endgame.</p>
        </div>
      </section>

      {open && selectedTrain && (
        <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/70 p-4" role="dialog" aria-modal="true" aria-labelledby="verify-title">
          <div className="max-h-[90dvh] w-full max-w-lg overflow-auto rounded-2xl border border-line bg-surface p-6 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="font-mono text-sm text-accent">QUICK PRESENCE CHECK</p>
                <h2 id="verify-title" className="mt-1 text-2xl font-semibold">Confirm this journey</h2>
                <p className="mt-2 text-sm text-muted">
                  {selectedTrain.name} · {journeyLabel(journey)} · {formatJourneyDate(journey.date)}
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  setFamily(null);
                }}
                aria-label="Close verification"
                className="rounded-lg px-2 text-2xl text-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
              >
                ×
              </button>
            </div>
            <p className="mt-4 rounded-xl border border-line bg-bg p-3 text-sm text-muted">
              A short physical or perceptual check confirms a person is present before ARHV holds the demo seat.
            </p>
            <div className="mt-6">
              {!family && <VerifyChooser onChoose={(choice) => setFamily(choice)} />}
              {family && (
                <button
                  type="button"
                  onClick={() => setFamily(null)}
                  className="mb-4 text-sm text-muted underline decoration-accent underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
                >
                  Choose another verification path
                </button>
              )}
              {family === "imu-v1" && <PhysicalWidget cohort={cohort} onVerified={verified} onFallback={() => setFamily("mdg-v1")} />}
              {family === "mdg-v1" && <PactWidget cohort={cohort} onVerified={verified} />}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
