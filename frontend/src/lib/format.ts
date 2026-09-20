export function pct(value: number): string {
  return `${(value * 100).toFixed(value < 0.1 ? 1 : 0)}%`;
}

export function ci(interval: [number, number]): string {
  return `[${pct(interval[0])}, ${pct(interval[1])}]`;
}

export function ms(value: number): string {
  return value > 0 ? `${Math.round(value)} ms` : "—";
}
