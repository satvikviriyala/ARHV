import { useEffect, useState } from "react";
import { api, ApiError, type Booking } from "../lib/api";

type Props = {
  token: string;
  onBooked?: (booking: Booking) => void;
};

export default function BookingCard({ token, onBooked }: Props) {
  const [booking, setBooking] = useState<Booking | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    void api
      .book(token)
      .then((result) => {
        if (active) {
          setBooking(result);
          onBooked?.(result);
        }
      })
      .catch((reason: unknown) => {
        if (!active) return;
        setError(reason instanceof ApiError ? reason.message : "The counter could not complete the booking.");
      });
    return () => {
      active = false;
    };
  }, [onBooked, token]);

  if (error) {
    return <div className="rounded-2xl border border-bad p-5 text-bad">{error}</div>;
  }
  if (!booking) {
    return <div className="rounded-2xl border border-line p-5 text-muted">Booking the last seat…</div>;
  }
  return (
    <div className="rounded-2xl border border-ok bg-surface p-5">
      <p className="text-sm uppercase tracking-wider text-ok">Seat held</p>
      <h3 className="mt-2 text-2xl font-semibold">{booking.counter}</h3>
      <p className="mt-2 font-mono text-muted">PNR {booking.pnr} · Seat {booking.seat}</p>
      <p className="mt-4 text-sm">
        Allowed by Cedar policy <code className="font-mono text-accent">{booking.policy}</code>
      </p>
      <p className="mt-1 text-sm text-muted">Assurance: {booking.assurance}</p>
    </div>
  );
}
