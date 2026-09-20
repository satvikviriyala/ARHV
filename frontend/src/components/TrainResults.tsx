import { ArrowRight, Clock3, ShieldCheck, TrainFront } from "lucide-react";
import { formatJourneyDate, journeyLabel, TRAIN_OPTIONS, type Journey, type TrainOption } from "../lib/rail";

type Props = {
  journey: Journey;
  onBook: (train: TrainOption) => void;
};

const money = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export default function TrainResults({ journey, onBook }: Props) {
  return (
    <section className="space-y-4" aria-labelledby="available-services">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="font-mono text-xs tracking-[0.18em] text-accent">AVAILABLE SERVICES</p>
          <h2 id="available-services" className="mt-1 text-2xl font-semibold">
            {journeyLabel(journey)}
          </h2>
          <p className="mt-1 text-sm text-muted">
            {formatJourneyDate(journey.date)} · {journey.travelClass} · {journey.quota}
          </p>
        </div>
        <p className="rounded-full border border-line px-3 py-1 text-xs text-muted">3 fictional services</p>
      </div>

      <div className="space-y-3">
        {TRAIN_OPTIONS.map((train) => (
          <article key={train.id} className="rounded-2xl border border-line bg-surface p-4 transition hover:border-accent sm:p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex min-w-0 items-start gap-3">
                <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-surface-2 text-accent">
                  <TrainFront size={22} aria-hidden="true" />
                </div>
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-lg font-semibold">{train.name}</h3>
                    <span className="font-mono text-xs text-muted">{train.code}</span>
                    {train.badge && <span className="rounded-full bg-accent/15 px-2 py-1 text-xs text-accent">{train.badge}</span>}
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
                    <span className="font-mono text-ink">{train.departure}</span>
                    <ArrowRight size={15} className="text-muted" aria-hidden="true" />
                    <span className="font-mono text-ink">{train.arrival}</span>
                    <span className="text-muted">{journey.to}</span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted">
                    <span className="inline-flex items-center gap-1">
                      <Clock3 size={14} aria-hidden="true" />
                      {train.duration}
                    </span>
                    <span>{train.seats} seats available</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between gap-4 border-t border-line pt-3 lg:min-w-52 lg:flex-col lg:items-end lg:border-0 lg:pt-0">
                <div className="text-left lg:text-right">
                  <p className="font-mono text-lg">{money.format(train.fare)}</p>
                  <p className="text-xs text-muted">per traveller</p>
                </div>
                <button
                  type="button"
                  onClick={() => onBook(train)}
                  className="rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-bg transition hover:brightness-110 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
                >
                  Book this journey
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>

      <p className="flex items-start gap-2 rounded-xl border border-line bg-surface p-3 text-xs text-muted">
        <ShieldCheck size={16} className="mt-0.5 shrink-0 text-ok" aria-hidden="true" />
        The selected journey is a fictional demo. A quick presence check happens before the seat is held.
      </p>
    </section>
  );
}
