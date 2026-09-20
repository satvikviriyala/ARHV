import { ArrowRightLeft, CalendarDays, ChevronDown, MapPin, Search } from "lucide-react";
import { todayIsoDate, type Journey } from "../lib/rail";

type Props = {
  journey: Journey;
  onChange: (journey: Journey) => void;
  onSubmit: () => void;
  compact?: boolean;
};

const fieldClass =
  "mt-2 w-full rounded-xl border border-line bg-bg px-3 py-3 text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent";

export default function JourneySearch({ journey, onChange, onSubmit, compact = false }: Props) {
  function update<K extends keyof Journey>(key: K, value: Journey[K]) {
    onChange({ ...journey, [key]: value });
  }

  function swapStations() {
    onChange({ ...journey, from: journey.to, to: journey.from });
  }

  return (
    <form
      className={`rounded-2xl border border-line bg-surface p-4 sm:p-5 ${compact ? "space-y-4" : "space-y-5"}`}
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
      aria-label="Search rail journeys"
    >
      <div className="grid gap-3 md:grid-cols-[1fr_auto_1fr] md:items-end">
        <label className="block text-sm">
          <span className="flex items-center gap-2 font-medium">
            <MapPin size={16} className="text-accent" aria-hidden="true" />
            From
          </span>
          <input
            className={fieldClass}
            value={journey.from}
            onChange={(event) => update("from", event.target.value)}
            list="rail-stations"
            autoComplete="off"
            required
          />
        </label>
        <button
          type="button"
          onClick={swapStations}
          aria-label="Swap origin and destination"
          className="flex size-11 items-center justify-center self-end rounded-xl border border-line text-muted transition hover:border-accent hover:text-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          <ArrowRightLeft size={17} aria-hidden="true" />
        </button>
        <label className="block text-sm">
          <span className="flex items-center gap-2 font-medium">
            <MapPin size={16} className="text-accent" aria-hidden="true" />
            To
          </span>
          <input
            className={fieldClass}
            value={journey.to}
            onChange={(event) => update("to", event.target.value)}
            list="rail-stations"
            autoComplete="off"
            required
          />
        </label>
      </div>

      <datalist id="rail-stations">
        <option value="Bengaluru" />
        <option value="Hyderabad" />
        <option value="Visakhapatnam" />
        <option value="Chennai" />
        <option value="Mysuru" />
      </datalist>

      <div className="grid gap-3 sm:grid-cols-3">
        <label className="block text-sm">
          <span className="flex items-center gap-2 font-medium">
            <CalendarDays size={16} className="text-accent" aria-hidden="true" />
            Travel date
          </span>
          <input
            className={fieldClass}
            type="date"
            min={todayIsoDate()}
            value={journey.date}
            onChange={(event) => update("date", event.target.value)}
            required
          />
        </label>
        <label className="relative block text-sm">
          <span className="font-medium">Class</span>
          <select
            className={`${fieldClass} appearance-none pr-9`}
            value={journey.travelClass}
            onChange={(event) => update("travelClass", event.target.value as Journey["travelClass"])}
          >
            <option>AC 2 Tier</option>
            <option>AC 3 Tier</option>
            <option>Sleeper</option>
          </select>
          <ChevronDown size={16} className="pointer-events-none absolute right-3 top-10 text-muted" aria-hidden="true" />
        </label>
        <label className="relative block text-sm">
          <span className="font-medium">Quota</span>
          <select
            className={`${fieldClass} appearance-none pr-9`}
            value={journey.quota}
            onChange={(event) => update("quota", event.target.value as Journey["quota"])}
          >
            <option>General</option>
            <option>Flexible travel</option>
            <option>Community access</option>
          </select>
          <ChevronDown size={16} className="pointer-events-none absolute right-3 top-10 text-muted" aria-hidden="true" />
        </label>
      </div>

      <button
        type="submit"
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-accent px-5 py-3 font-semibold text-bg transition hover:brightness-110 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        <Search size={18} aria-hidden="true" />
        Search trains
      </button>
    </form>
  );
}
