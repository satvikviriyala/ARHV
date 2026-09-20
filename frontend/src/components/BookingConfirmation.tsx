import { useEffect, useRef } from "react";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import { Link, useLocation } from "react-router";
import { formatJourneyDate, journeyLabel, type Journey, type TrainOption } from "../lib/rail";
import type { Booking } from "../lib/api";

type ConfirmationState = {
  booking: Booking;
  journey: Journey;
  train: TrainOption;
};

function readConfirmationState(value: unknown): ConfirmationState | null {
  if (!value || typeof value !== "object") return null;
  const candidate = value as Partial<ConfirmationState>;
  if (!candidate.booking || !candidate.journey || !candidate.train) return null;
  return {
    booking: candidate.booking,
    journey: candidate.journey,
    train: candidate.train,
  };
}

export default function BookingConfirmation() {
  const location = useLocation();
  const headingId = "booking-confirmed-heading";
  const heading = useRef<HTMLHeadingElement>(null);
  const state = readConfirmationState(location.state);
  useEffect(() => {
    heading.current?.focus();
  }, []);

  if (!state) {
    return (
      <section className="mx-auto max-w-xl space-y-4" aria-labelledby={headingId}>
        <p className="font-mono text-xs tracking-[0.18em] text-accent">ARHV RAIL · FICTIONAL DEMO</p>
        <h1 id={headingId} ref={heading} tabIndex={-1} className="text-3xl font-semibold">
          No demo booking is open
        </h1>
        <p className="text-muted">Start a fictional journey from the ARHV Rail counter to see its confirmation details.</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-3 font-semibold text-bg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          <ArrowLeft size={18} aria-hidden="true" />
          Return to ARHV Rail
        </Link>
      </section>
    );
  }

  const { booking, journey, train } = state;
  return (
    <section className="mx-auto max-w-2xl space-y-6" aria-labelledby={headingId}>
      <div className="rounded-3xl border border-ok bg-surface p-6 sm:p-8">
        <div className="flex items-start gap-4">
          <CheckCircle2 className="mt-1 shrink-0 text-ok" size={30} aria-hidden="true" />
          <div>
            <p className="font-mono text-xs tracking-[0.18em] text-accent">ARHV RAIL · FICTIONAL DEMO</p>
            <h1 id={headingId} ref={heading} className="mt-2 text-3xl font-semibold" tabIndex={-1}>
              Your ticket is confirmed
            </h1>
            <p className="mt-3 text-muted" role="status" aria-live="polite">
              Your fictional ARHV Rail demo booking is confirmed. No external ticket was issued.
            </p>
          </div>
        </div>

        <dl className="mt-8 grid gap-4 rounded-2xl bg-surface-2 p-4 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-muted">Booking reference</dt>
            <dd className="mt-1 font-mono text-lg">{booking.pnr}</dd>
          </div>
          <div>
            <dt className="text-muted">Service</dt>
            <dd className="mt-1 font-medium">
              {train.name} <span className="font-mono text-xs text-muted">· {train.code}</span>
            </dd>
          </div>
          <div>
            <dt className="text-muted">Route</dt>
            <dd className="mt-1 font-medium">{journeyLabel(journey)}</dd>
          </div>
          <div>
            <dt className="text-muted">Travel date</dt>
            <dd className="mt-1 font-medium">{formatJourneyDate(journey.date)}</dd>
          </div>
          <div>
            <dt className="text-muted">Class</dt>
            <dd className="mt-1 font-medium">{journey.travelClass}</dd>
          </div>
          <div>
            <dt className="text-muted">Seat</dt>
            <dd className="mt-1 font-mono">{booking.seat}</dd>
          </div>
        </dl>

        <p className="mt-5 text-sm text-muted">
          Protected by Cedar policy <code className="font-mono text-accent">{booking.policy}</code> · assurance{" "}
          <span className="font-mono">{booking.assurance}</span>
        </p>
      </div>

      <Link
        to="/"
        className="inline-flex items-center gap-2 rounded-xl border border-line px-5 py-3 font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        <ArrowLeft size={18} aria-hidden="true" />
        Book another journey
      </Link>
    </section>
  );
}
