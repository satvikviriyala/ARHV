"""Render the 'screenshot vs motion' figure used in the README, About page and demo video.

Left column: one frame (what any screenshot-based agent sees). Right column: motion-consistency map
(what the human visual system extracts). Dev-only deps: numpy, Pillow.
Usage: python scripts/make_viz.py --out docs/assets/screenshot-vs-motion.png [--core backend/layers/core/pact_core]
"""

import argparse
import os
import secrets
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=os.path.join(ROOT, "docs", "assets", "screenshot-vs-motion.png"))
    p.add_argument("--core", default=os.path.join(ROOT, "backend", "layers", "core", "pact_core"))
    p.add_argument("--rounds", type=int, default=3)
    a = p.parse_args()
    sys.path.insert(0, a.core)
    import mdg  # noqa: E402

    seed = secrets.token_bytes(32)
    spec_rng, tex, noise = mdg.KeyedRng(seed, "spec"), mdg.KeyedRng(seed, "tex"), mdg.KeyedRng(seed, "noise")
    rows = []
    for _ in range(a.rounds):
        spec = mdg.make_round_spec(spec_rng)
        frames = mdg.render_round(spec, tex, noise, frames=24)
        single = np.zeros((mdg.H, mdg.W), np.uint8)
        for x, y in frames[0]:
            single[y : y + mdg.DOT, x : x + mdg.DOT] = 235
        acc = np.zeros((mdg.H, mdg.W), np.float32)
        for t in range(len(frames) - 1):
            nxt = set(frames[t + 1])
            for x, y in frames[t]:
                f = ((x + spec.fig_v[0]) % mdg.SPAN, (y + spec.fig_v[1]) % mdg.SPAN) in nxt
                g = ((x + spec.gnd_v[0]) % mdg.SPAN, (y + spec.gnd_v[1]) % mdg.SPAN) in nxt
                acc[y : y + mdg.DOT, x : x + mdg.DOT] += float(f) - float(g)
        k = 7
        pad = np.pad(acc, k // 2, mode="edge")
        sm = np.lib.stride_tricks.sliding_window_view(pad, (k, k)).mean(axis=(2, 3))
        vis = ((sm - sm.min()) / (np.ptp(sm) + 1e-9) * 255).astype(np.uint8)
        gap = np.full((mdg.H, 6), 60, np.uint8)
        rows.append(np.hstack([single, gap, vis]))
        rows.append(np.full((6, rows[-1].shape[1]), 60, np.uint8))
    img = np.vstack(rows[:-1])
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    Image.fromarray(img).resize((img.shape[1] * 3, img.shape[0] * 3), Image.NEAREST).save(a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
