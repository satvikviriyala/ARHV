import { useCallback, useState } from "react";
import { useSearchParams } from "react-router";
import BookingCard from "../components/BookingCard";
import DevPanel from "../components/DevPanel";
import PhysicalWidget from "../components/PhysicalWidget";
import PactWidget from "../components/PactWidget";
import { getCohort } from "../lib/cohort";

export default function Phone() {
  const [params] = useSearchParams();
  const cohort = params.get("cohort") ?? getCohort();
  const [token, setToken] = useState("");
  const [metrics, setMetrics] = useState<Record<string, unknown>>({});
  const [fallback, setFallback] = useState(false);
  const [booked, setBooked] = useState(false);
  const onVerified = useCallback((newToken: string, details?: { assurance?: "motion" | "physical"; metrics?: Record<string, unknown> }) => {
    setToken(newToken);
    setMetrics(details?.metrics ?? {});
  }, []);
  const onBooked = useCallback(() => setBooked(true), []);
  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div>
        <p className="font-mono text-sm tracking-widest text-accent">ARHV · PHONE VERIFIER</p>
        <h1 className="mt-3 text-3xl font-semibold">Tilt your phone to verify</h1>
        <p className="mt-3 text-muted">Keep this page in portrait. The server chooses three fresh rings for this request.</p>
      </div>
      {!token && !fallback && <PhysicalWidget cohort={cohort} onVerified={onVerified} onFallback={() => setFallback(true)} />}
      {!token && fallback && (
        <div className="rounded-2xl border border-line p-4">
          <p className="mb-4 text-sm text-muted">Motion sensors are unavailable. You can use the perceptual path instead.</p>
          <PactWidget cohort={cohort} onVerified={onVerified} />
        </div>
      )}
      {token && (
        <>
          <BookingCard token={token} onBooked={onBooked} />
          <DevPanel token={token} metrics={metrics} booked={booked} />
        </>
      )}
    </div>
  );
}
