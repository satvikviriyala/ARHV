import { describe, expect, it } from "vitest";
import { decodeFrames, pingPongIndex } from "./mdg";

function encode(frames: number[][][]): string {
  const bytes: number[] = [];
  for (const f of frames) {
    bytes.push((f.length >> 8) & 255, f.length & 255);
    for (const [x, y] of f) bytes.push(x!, y!);
  }
  return btoa(String.fromCharCode(...bytes));
}

describe("decodeFrames", () => {
  it("round-trips the server wire format", () => {
    const frames = decodeFrames(encode([[[1, 2], [3, 4]], [[158, 0]]]));
    expect(frames.length).toBe(2);
    expect(Array.from(frames[0]!)).toEqual([1, 2, 3, 4]);
    expect(Array.from(frames[1]!)).toEqual([158, 0]);
  });
});

describe("pingPongIndex", () => {
  it("bounces without jumping", () => {
    expect([0, 1, 2, 3, 4, 5, 6].map((t) => pingPongIndex(t, 4))).toEqual([0, 1, 2, 3, 2, 1, 0]);
  });
});
