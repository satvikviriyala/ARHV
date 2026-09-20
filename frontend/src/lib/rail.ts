export type TravelClass = "AC 2 Tier" | "AC 3 Tier" | "Sleeper";
export type TravelQuota = "General" | "Flexible travel" | "Community access";

export type Journey = {
  from: string;
  to: string;
  date: string;
  travelClass: TravelClass;
  quota: TravelQuota;
};

export type TrainOption = {
  id: string;
  code: string;
  name: string;
  departure: string;
  arrival: string;
  duration: string;
  seats: number;
  fare: number;
  badge?: string;
};

function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

export function todayIsoDate(): string {
  return isoDate(new Date());
}

export function tomorrowIsoDate(): string {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return isoDate(tomorrow);
}

export const DEFAULT_JOURNEY: Journey = {
  from: "Bengaluru",
  to: "Visakhapatnam",
  date: tomorrowIsoDate(),
  travelClass: "AC 2 Tier",
  quota: "General",
};

export const TRAIN_OPTIONS: TrainOption[] = [
  {
    id: "coastal-dawn",
    code: "AR 204",
    name: "Coastal Dawn",
    departure: "06:40",
    arrival: "20:25",
    duration: "13h 45m",
    seats: 12,
    fare: 1860,
    badge: "Best departure",
  },
  {
    id: "horizon-nightline",
    code: "AR 518",
    name: "Horizon Nightline",
    departure: "21:10",
    arrival: "11:15 +1",
    duration: "14h 05m",
    seats: 4,
    fare: 1540,
    badge: "Quiet ride",
  },
  {
    id: "southern-arc",
    code: "AR 731",
    name: "Southern Arc",
    departure: "14:20",
    arrival: "04:55 +1",
    duration: "14h 35m",
    seats: 7,
    fare: 1290,
  },
];

export function formatJourneyDate(date: string): string {
  if (!date) return "Choose a date";
  const parsed = new Date(`${date}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return date;
  return new Intl.DateTimeFormat("en-IN", {
    weekday: "short",
    day: "numeric",
    month: "short",
  }).format(parsed);
}

export function journeyLabel(journey: Journey): string {
  return `${journey.from} → ${journey.to}`;
}
