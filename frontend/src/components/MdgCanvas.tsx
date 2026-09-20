import { useEffect, useMemo, useRef, useState } from "react";
import { decodeFrames, pingPongIndex } from "../lib/mdg";
import type { MdgRound } from "../lib/api";

type Props = {
  round: MdgRound;
  fps: number;
  dot: number;
  width: number;
  height: number;
  autoplay?: boolean;
  onFirstFrame?: () => void;
};

export default function MdgCanvas({
  round,
  fps,
  dot,
  width,
  height,
  autoplay = true,
  onFirstFrame,
}: Props) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [playing, setPlaying] = useState(() => {
    if (typeof window === "undefined") return autoplay;
    return autoplay && !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  });
  const frames = useMemo(() => decodeFrames(round.frames), [round.frames]);

  useEffect(() => {
    const element = canvas.current;
    if (!element || frames.length === 0) return;
    const context = element.getContext("2d");
    if (!context) return;
    let frameId = 0;
    let first = true;
    let started = performance.now();
    let last = -1;

    const draw = (index: number) => {
      if (index === last) return;
      last = index;
      context.fillStyle = "#0b0d12";
      context.fillRect(0, 0, width, height);
      context.fillStyle = "#e6e8ee";
      const frame = frames[index]!;
      for (let i = 0; i + 1 < frame.length; i += 2) {
        context.fillRect(frame[i]!, frame[i + 1]!, dot, dot);
      }
      if (first) {
        first = false;
        onFirstFrame?.();
      }
    };

    const animate = (now: number) => {
      draw(pingPongIndex(Math.floor(((now - started) * fps) / 1000), frames.length));
      frameId = requestAnimationFrame(animate);
    };
    const pause = () => {
      if (document.hidden) cancelAnimationFrame(frameId);
      else {
        started = performance.now();
        frameId = requestAnimationFrame(animate);
      }
    };
    draw(0);
    if (playing) {
      document.addEventListener("visibilitychange", pause);
      frameId = requestAnimationFrame(animate);
    }
    return () => {
      cancelAnimationFrame(frameId);
      document.removeEventListener("visibilitychange", pause);
    };
  }, [dot, fps, frames, height, onFirstFrame, playing, width]);

  return (
    <div className="flex flex-col items-center gap-3">
      <canvas
        ref={canvas}
        width={width}
        height={height}
        role="img"
        aria-label="Animated puzzle: a shape is hidden in moving dots. If you can't use motion puzzles, choose Verify with your account."
        className="aspect-square w-[min(88vw,420px)] rounded-2xl border border-line [image-rendering:pixelated]"
      />
      {!playing && (
        <button
          type="button"
          onClick={() => setPlaying(true)}
          className="rounded-xl border border-accent px-4 py-2 text-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Play puzzle
        </button>
      )}
    </div>
  );
}
