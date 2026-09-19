// Decoder for the MDG wire format: per frame [uint16 BE count][count x (uint8 x, uint8 y)], whole round base64.
export type Frame = Uint8Array; // flat [x0, y0, x1, y1, ...]

export function decodeFrames(b64: string): Frame[] {
  const bin = atob(b64);
  const raw = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) raw[i] = bin.charCodeAt(i);
  const frames: Frame[] = [];
  let i = 0;
  while (i + 2 <= raw.length) {
    const n = (raw[i]! << 8) | raw[i + 1]!;
    i += 2;
    frames.push(raw.subarray(i, i + 2 * n));
    i += 2 * n;
  }
  return frames;
}

/** Ping-pong frame index: 0..n-1..1..0.. so playback never jumps. */
export function pingPongIndex(tick: number, n: number): number {
  if (n <= 1) return 0;
  const period = 2 * n - 2;
  const k = ((tick % period) + period) % period;
  return k < n ? k : period - k;
}
