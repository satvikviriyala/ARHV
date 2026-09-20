import { useEffect, useState } from "react";
import { api, ApiError, type Booking } from "../lib/api";
import { formatJourneyDate, journeyLabel, type Journey, type TrainOption } from "../lib/rail";
import VerificationFailure from "./VerificationFailure";

type Props = {
  token: string;
  journey?: Journey;
  train?: TrainOption | null;
  onBooked?: (booking: Booking) => void;
  onAuthorizationError?: (error: ApiError) => void;
  onRetry: () => void;
  sensorOnly?: boolean;
};

export default function BookingCard({ token, journey, train, onBooked, onAuthorizationError, onRetry, sensorOnly = false }: Props) {
  const [booking, setBooking] = useState<Booking | null>(null);
  const [error, setError] = useState("");
  const [authorizationFailed, setAuthorizationFailed] = useState(false);

  useEffect(() => {
    let active = true;
    void api
      .book(token)
      .then((result) => {
        if (active) {
          setBooking(result);
          onBooked?.(result);
        }
      }, (reason: unknown) => {
        if (!active) return;
        if (reason instanceof ApiError && (reason.status === 401 || reason.status === 403)) {
          setAuthorizationFailed(true);
          onAuthorizationError?.(reason);
          return;
        }
        setError(reason instanceof ApiError ? reason.message : "The counter could not complete the booking.");
      });
    return () => {
      active = false;
    };
  }, [onAuthorizationError, onBooked, token]);

  if (authorizationFailed) {
    return (
      <VerificationFailure
        onRetry={onRetry}
        sensorOnly={sensorOnly}
        context="The booking was not completed. Start a fresh check before trying this journey again."
      />
    );
  }
  if (error) {
    return <div className="rounded-2xl border border-bad p-5 text-bad">{error}</div>;
  }
  if (!booking) {
    return <div className="rounded-2xl border border-line p-5 text-muted">Confirming your selected journey…</div>;
  }
  return (
    <div className="rounded-2xl border border-ok bg-surface p-5" aria-live="polite">
      <p className="text-sm uppercase tracking-wider text-ok">Journey confirmed</p>
      <h3 className="mt-2 text-2xl font-semibold">{train?.name ?? booking.counter}</h3>
      {journey && (
        <p className="mt-1 text-sm text-muted">
          {train?.code ? `${train.code} · ` : ""}
          {journeyLabel(journey)}
        </p>
      )}
      <div className="mt-4 grid gap-3 rounded-xl bg-surface-2 p-4 text-sm sm:grid-cols-3">
        <div>
          <p className="text-xs text-muted">Travel date</p>
          <p className="mt-1 font-medium">{journey ? formatJourneyDate(journey.date) : "Demo date"}</p>
        </div>
        <div>
          <p className="text-xs text-muted">PNR</p>
          <p className="mt-1 font-mono">{booking.pnr}</p>
        </div>
        <div>
          <p className="text-xs text-muted">Seat</p>
          <p className="mt-1 font-mono">{booking.seat}</p>
        </div>
      </div>
      <p className="mt-4 text-sm">
        Allowed by Cedar policy <code className="font-mono text-accent">{booking.policy}</code>
      </p>
      <p className="mt-1 text-sm text-muted">Assurance: {booking.assurance}</p>
    </div>
  );
}
