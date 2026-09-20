import { useCallback, useState } from "react";
import { Link } from "react-router";
import { useSearchParams } from "react-router";
import BookingCard from "../components/BookingCard";
import DevPanel from "../components/DevPanel";
import JourneySearch from "../components/JourneySearch";
import PhysicalWidget from "../components/PhysicalWidget";
import PactWidget from "../components/PactWidget";
import { getCohort } from "../lib/cohort";
import { DEFAULT_JOURNEY, formatJourneyDate, journeyLabel, TRAIN_OPTIONS, type Journey } from "../lib/rail";

export default function Phone() {
  const [params] = useSearchParams();
  const cohort = params.get("cohort") ?? getCohort();
  const [journey, setJourney] = useState<Journey>(DEFAULT_JOURNEY);
  const [editing, setEditing] = useState(false);
  const [token, setToken] = useState("");
  const [metrics, setMetrics] = useState<Record<string, unknown>>({});
  const [fallback, setFallback] = useState(false);
  const [booked, setBooked] = useState(false);
  const train = TRAIN_OPTIONS[0]!;
  const onVerified = useCallback((newToken: string, details?: { assurance?: "motion" | "physical"; metrics?: Record<string, unknown> }) => {
    setToken(newToken);
    setMetrics(details?.metrics ?? {});
  }, []);
  const onBooked = useCallback(() => setBooked(true), []);
  return (
    <div className="mx-auto max-w-lg space-y-6">
      <section className="rounded-2xl border border-line bg-surface p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="font-mono text-xs tracking-[0.18em] text-accent">ARHV RAIL · PHONE</p>
            <h1 className="mt-2 text-3xl font-semibold">Quick presence check</h1>
          </div>
          {!token && (
            <button
              type="button"
              onClick={() => setEditing((value) => !value)}
              className="rounded-lg border border-line px-3 py-2 text-xs text-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              {editing ? "Close" : "Edit journey"}
            </button>
          )}
        </div>
        <p className="mt-3 text-muted">Tilt your phone gently to confirm this journey. Keep the page in portrait while the server chooses three fresh rings.</p>
        <div className="mt-4 rounded-xl border border-line bg-bg p-4">
          <p className="text-xs uppercase tracking-wider text-muted">Selected journey</p>
          <p className="mt-2 font-medium">{journeyLabel(journey)}</p>
          <p className="mt-1 text-sm text-muted">{formatJourneyDate(journey.date)} · {train.name} · {journey.travelClass}</p>
        </div>
        {editing && (
          <div className="mt-4">
            <JourneySearch journey={journey} onChange={setJourney} onSubmit={() => setEditing(false)} compact />
          </div>
        )}
      </section>
      {!token && !fallback && <PhysicalWidget cohort={cohort} onVerified={onVerified} onFallback={() => setFallback(true)} />}
      {!token && fallback && (
        <div className="rounded-2xl border border-line p-4">
          <p className="mb-4 text-sm text-muted">Motion sensors aren&apos;t available here. You can use the moving-shape path instead.</p>
          <PactWidget cohort={cohort} onVerified={onVerified} />
          <Link
            to="/account"
            className="mt-4 block text-center text-sm text-muted underline decoration-accent underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Can&apos;t use a puzzle? Verify with your account instead.
          </Link>
        </div>
      )}
      {token && (
        <>
          <BookingCard token={token} journey={journey} train={train} onBooked={onBooked} />
          <DevPanel token={token} metrics={metrics} booked={booked} />
        </>
      )}
    </div>
  );
}
