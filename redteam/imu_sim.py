"""Synthetic phone-motion traces for imu-v1: used by tests AND by the red team (scripts/imu_attack_demo.py).

`physical_trace` produces a trace that obeys every physics check (orientation, gravity direction, gyro, timing,
continuity). That it passes the verifier is the point: over an unattested web channel, a good enough simulator is
indistinguishable from a real phone. Only vendor attestation of the sensor stream closes that gap.
The other generators are the cheap spoofs real bots use (orientation-only, flat, teleporting, replayed).
"""

from __future__ import annotations

import math
import random

try:
    from pact_core import imu
except ImportError:  # running outside pytest: make the layer importable
    import os
    import sys

    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "layers", "core")
    )
    from pact_core import imu

G = imu.G


def _min_jerk(s: float) -> float:
    return 10 * s**3 - 15 * s**4 + 6 * s**5


def _waypoints(challenge: dict, beta0: float, gamma0: float, rng: random.Random):
    """Piecewise path: baseline hold, then move -> hold for each target."""
    segs = [("hold", (beta0, gamma0), (beta0, gamma0), challenge["baselineMs"] + 250)]
    cur = (beta0, gamma0)
    for t in challenge["targets"]:
        goal = (beta0 + t["dBeta"] + rng.uniform(-2, 2), gamma0 + t["dGamma"] + rng.uniform(-2, 2))
        segs.append(("move", cur, goal, rng.uniform(650, 1000)))
        segs.append(("hold", goal, goal, t["holdMs"] + rng.uniform(250, 450)))
        cur = goal
    return segs


def physical_trace(
    challenge: dict,
    challenge_id: str,
    *,
    ios: bool = False,
    seed: int = 7,
    hz: float = 60.0,
    beta0: float = 42.0,
    gamma0: float = 1.5,
) -> dict:
    """A physically coherent trace (what a real phone - or a careful simulator - produces)."""
    rng = random.Random(seed)
    segs = _waypoints(challenge, beta0, gamma0, rng)
    total = sum(s[3] for s in segs)
    samples, t = [], 0.0
    ph = [rng.uniform(0, 6.28) for _ in range(4)]
    prev = None
    alpha = 30.0
    while t <= total:
        # locate segment
        acc, seg = 0.0, segs[-1]
        for s in segs:
            if t < acc + s[3]:
                seg = s
                break
            acc += s[3]
        u = min(1.0, max(0.0, (t - acc) / seg[3]))
        w = _min_jerk(u) if seg[0] == "move" else 0.0
        b = seg[1][0] + (seg[2][0] - seg[1][0]) * w
        g = seg[1][1] + (seg[2][1] - seg[1][1]) * w
        # physiological tremor (~8-11 Hz, fraction of a degree) + slow drift
        ts = t / 1000.0
        b += 0.35 * math.sin(2 * math.pi * 9.1 * ts + ph[0]) + 0.2 * math.sin(2 * math.pi * 3.3 * ts + ph[1])
        g += 0.35 * math.sin(2 * math.pi * 10.2 * ts + ph[2]) + 0.2 * math.sin(2 * math.pi * 2.7 * ts + ph[3])
        alpha += 0.004 * (1 if rng.random() < 0.5 else -1)
        if prev is None:
            db = dg = da = 0.0
        else:
            dts = (t - prev[0]) / 1000.0
            db, dg, da = (b - prev[1]) / dts, (g - prev[2]) / dts, 0.0
        br, gr = math.radians(b), math.radians(g)
        wx = db * math.cos(gr) - da * math.cos(br) * math.sin(gr)
        wy = da * math.sin(br) + dg
        wz = db * math.sin(gr) + da * math.cos(br) * math.cos(gr)
        lin = 0.6 if seg[0] == "move" else 0.12  # hand's linear acceleration (m/s^2)
        gx = -G * math.cos(br) * math.sin(gr) + rng.gauss(0, lin)
        gy = G * math.sin(br) + rng.gauss(0, lin)
        gz = G * math.cos(br) * math.cos(gr) + rng.gauss(0, lin)
        sgn = -1.0 if ios else 1.0
        samples.append(
            [
                round(t, 1),
                round(b, 1),
                round(g, 1),
                round(alpha, 1),
                round(sgn * gx, 1),
                round(sgn * gy, 1),
                round(sgn * gz, 1),
                round(wz + rng.gauss(0, 1.2), 1),
                round(wx + rng.gauss(0, 1.2), 1),
                round(wy + rng.gauss(0, 1.2), 1),
            ]
        )
        prev = (t, b, g)
        t += 1000.0 / hz + rng.uniform(-1.2, 1.2)
    return {"challengeId": challenge_id, "nonce": challenge["nonce"], "samples": samples}


# ------------------------------------------------------------------ cheap spoofs (what real bots actually send)
def orientation_only_spoof(trace: dict) -> dict:
    """Fake orientation stream (e.g. DevTools sensor emulation) with no real accelerometer/gyro behind it."""
    out = dict(trace)
    out["samples"] = [s[:4] + [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] for s in trace["samples"]]
    return out


def no_gyro_spoof(trace: dict) -> dict:
    """Orientation + matching gravity, but a dead gyroscope."""
    out = dict(trace)
    out["samples"] = [s[:7] + [0.0, 0.0, 0.0] for s in trace["samples"]]
    return out


def mismatched_gravity_spoof(trace: dict) -> dict:
    """Orientation from one motion, gravity from another (phone lying flat on a table)."""
    out = dict(trace)
    out["samples"] = [s[:4] + [0.0, 0.2, 9.8] + s[7:] for s in trace["samples"]]
    return out


def teleport_spoof(challenge: dict, challenge_id: str) -> dict:
    """Jump straight to each target (scripted bot): no motion in between."""
    tr = physical_trace(challenge, challenge_id, seed=3)
    out = dict(tr)
    samples = [list(s) for s in tr["samples"]]
    b0, g0 = samples[0][1], samples[0][2]
    k = 0
    for i, s in enumerate(samples):
        if i and i % 60 == 0 and k < len(challenge["targets"]):
            k += 1
        if k:
            tgt = challenge["targets"][k - 1]
            s[1], s[2] = round(b0 + tgt["dBeta"], 1), round(g0 + tgt["dGamma"], 1)
    out["samples"] = samples
    return out
