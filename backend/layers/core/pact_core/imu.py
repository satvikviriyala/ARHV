"""imu-v1: physical-motion challenge (phone tilt) - generator + physics verifier. Stdlib only.

The user tilts their phone to steer a dot through server-chosen targets. The server does NOT trust the client's
"target reached" claim: it re-derives everything from the raw sensor trace and checks that the trace is
physically coherent. The checks are cross-sensor physics, not "human jitter" behaviour classification:

  binding      trace echoes this challenge's id + nonce (fresh per challenge, so recordings can't be replayed)
  timing       monotonic timestamps, plausible sensor rate, no long gaps, duration within limits
  gravity      |accelerationIncludingGravity| ~ 9.81 m/s^2 (a real accelerometer always feels gravity)
  tilt         the tilt implied by the gravity vector matches the reported orientation (beta, gamma)
  gyro         the gyroscope's rotation rate co-varies with the rate of change of orientation
  continuity   no teleports between consecutive samples
  targets      the path holds each randomised target, in order, for its hold time

What this does NOT prove: that the sensors are real. A browser/automation stack can synthesise a stream that
obeys all of the above (see test_physically_consistent_synthetic_trace_passes). Closing that gap needs the
device vendor to attest the sensor stream (secure sensor hub + TPM/Secure Enclave/StrongBox signature over the
server nonce), which is exactly ARHV's "vendor-supported physical verification" proposal (docs/PHYSICAL.md).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

try:  # inside the PactCoreLayer
    from .mdg import KeyedRng
except ImportError:  # running from a flat directory (reference/tests)
    from mdg import KeyedRng

FAMILY = "imu-v1"
N_TARGETS = 3  # tilt targets per challenge (plus an implicit start baseline)
TARGET_TILT = (16.0, 26.0)  # degrees of tilt offset from the user's own baseline
TARGET_RADIUS = 8.0  # degrees: how close the dot must be to count as "on target"
HOLD_MS = 450  # hold inside each target
BASELINE_MS = 600  # initial comfortable hold used as the user's own zero
MAX_DURATION_MS = 30_000  # whole challenge must finish in 30 s
TILT_ERROR_MAX_DEG = 18.0  # modest budget for browser sensor-fusion/calibration skew
MIN_SAMPLES, MAX_SAMPLES = 30, 4_000
G = 9.80665

# sample layout sent by the client (compact arrays keep the payload ~100 KB for 30 s at 60 Hz)
# [t_ms, beta, gamma, alpha|None, gx, gy, gz, rAlpha, rBeta, rGamma]
T, BETA, GAMMA, ALPHA, GX, GY, GZ, RA, RB, RG = range(10)

DIRECTIONS = [(math.cos(k * math.pi / 4), math.sin(k * math.pi / 4)) for k in range(8)]  # (dGamma, dBeta) unit


def generate_challenge(seed: bytes) -> dict:
    """Random, fresh targets + nonce. Targets are public by design: they ARE the instructions. Security comes
    from freshness (a recording visits the wrong targets), timing and physics, not from secrecy."""
    rng = KeyedRng(seed, "imu")
    targets, last_dir = [], None
    for _ in range(N_TARGETS):
        d = rng.randbelow(8)
        while last_dir is not None and (d == last_dir or d == (last_dir + 4) % 8 and rng.random() < 0.5):
            d = rng.randbelow(8)
        last_dir = d
        mag = rng.uniform(*TARGET_TILT)
        ux, uy = DIRECTIONS[d]
        targets.append(
            {"dGamma": round(ux * mag, 1), "dBeta": round(uy * mag, 1), "radius": TARGET_RADIUS, "holdMs": HOLD_MS}
        )
    nonce = bytes(rng.randbelow(256) for _ in range(16)).hex()
    return {
        "family": FAMILY,
        "nonce": nonce,
        "targets": targets,
        "baselineMs": BASELINE_MS,
        "maxDurationMs": MAX_DURATION_MS,
        "sampleHz": 60,
    }


# ----------------------------------------------------------------------------------------------- helpers
def _median(xs: list[float]) -> float:
    s = sorted(xs)
    n = len(s)
    return 0.0 if n == 0 else (s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2]))


def _pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    if n < 5:
        return 0.0
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 1e-9 or vb <= 1e-9:
        return 0.0
    return sum((x - ma) * (y - mb) for x, y in zip(a, b, strict=True)) / math.sqrt(va * vb)


def _angdiff(a: float, b: float) -> float:
    """Smallest signed difference a-b in degrees."""
    return (a - b + 180.0) % 360.0 - 180.0


def _smooth(xs: list[float], k: int = 2) -> list[float]:
    out = []
    for i in range(len(xs)):
        lo, hi = max(0, i - k), min(len(xs), i + k + 1)
        out.append(sum(xs[lo:hi]) / (hi - lo))
    return out


def tilt_from_gravity(gx: float, gy: float, gz: float) -> tuple[float, float]:
    """(beta, gamma) in degrees implied by the gravity reaction vector, W3C Z-X'-Y'' convention with the
    Android sign convention (device flat, screen up => g ~ (0, 0, +9.81)). iOS reports the opposite sign;
    callers try both. Derivation: g_dev = (-g cosB sinG, g sinB, g cosB cosG)."""
    beta = math.degrees(math.atan2(gy, math.hypot(gx, gz)))
    gamma = math.degrees(math.atan2(-gx, gz))
    return beta, gamma


@dataclass
class ImuResult:
    passed: bool
    reasons: list[str] = field(default_factory=list)  # failed check names (empty when passed)
    metrics: dict = field(default_factory=dict)  # numbers for logs / explain / evaluation


# ----------------------------------------------------------------------------------------------- verifier
def verify(challenge: dict, challenge_id: str, trace: dict) -> ImuResult:
    reasons: list[str] = []
    m: dict = {}

    # binding ----------------------------------------------------------------------------------------------
    if trace.get("challengeId") != challenge_id or trace.get("nonce") != challenge.get("nonce"):
        return ImuResult(False, ["binding"], m)
    raw = trace.get("samples")
    if not isinstance(raw, list) or not (MIN_SAMPLES <= len(raw) <= MAX_SAMPLES):
        return ImuResult(False, ["size"], {"n": len(raw) if isinstance(raw, list) else 0})
    samples: list[list[float]] = []
    for s in raw:
        if not isinstance(s, list) or len(s) != 10:
            return ImuResult(False, ["format"], m)
        row = []
        for i, v in enumerate(s):
            if v is None and i == ALPHA:
                row.append(float("nan"))
            elif isinstance(v, (int, float)) and math.isfinite(v):
                row.append(float(v))
            else:
                return ImuResult(False, ["format"], m)
        samples.append(row)
    n = len(samples)
    m["n"] = n

    # timing -----------------------------------------------------------------------------------------------
    ts = [s[T] for s in samples]
    dts = [b - a for a, b in zip(ts, ts[1:], strict=False)]
    if any(dt <= 0 for dt in dts):
        return ImuResult(False, ["timing"], m)
    duration = ts[-1] - ts[0]
    med_dt, max_gap = _median(dts), max(dts)
    m.update(durationMs=round(duration), medianDtMs=round(med_dt, 2), maxGapMs=round(max_gap))
    mean_dt = sum(dts) / len(dts)
    m["dtJitterMs"] = round(math.sqrt(sum((d - mean_dt) ** 2 for d in dts) / len(dts)), 3)  # risk signal only
    min_duration = challenge["baselineMs"] + N_TARGETS * HOLD_MS * 0.8
    if (
        not (8.0 <= med_dt <= 120.0)
        or max_gap > 750.0
        or not (min_duration <= duration <= challenge["maxDurationMs"] + 2000)
    ):
        reasons.append("timing")

    betas = [s[BETA] for s in samples]
    gammas = [s[GAMMA] for s in samples]

    # continuity: a hand-held phone can't teleport; limit angular speed between consecutive samples ------------
    max_jump, max_speed = 0.0, 0.0
    for i in range(1, n):
        jump = max(abs(_angdiff(betas[i], betas[i - 1])), abs(_angdiff(gammas[i], gammas[i - 1])))
        max_jump = max(max_jump, jump)
        max_speed = max(max_speed, jump / (dts[i - 1] / 1000.0))
    m["maxJumpDeg"], m["maxSpeedDegS"] = round(max_jump, 1), round(max_speed)
    if max_jump > 30.0 or max_speed > 900.0:
        reasons.append("continuity")

    # gravity magnitude --------------------------------------------------------------------------------------
    mags = [math.sqrt(s[GX] ** 2 + s[GY] ** 2 + s[GZ] ** 2) for s in samples]
    frac_g = sum(1 for g in mags if 7.5 <= g <= 12.5) / n
    m["gravityFrac"] = round(frac_g, 3)
    if frac_g < 0.8:
        reasons.append("gravity")

    # tilt consistency: orientation vs gravity direction (quasi-static samples; try both sign conventions) ----
    rates = [math.sqrt(s[RA] ** 2 + s[RB] ** 2 + s[RG] ** 2) for s in samples]
    quasi = [i for i in range(n) if 8.3 <= mags[i] <= 11.3 and rates[i] < 60.0 and abs(betas[i]) < 80.0]
    m["quasiStatic"] = len(quasi)
    best_err, best_sign = float("inf"), 1
    for sign in (1, -1):
        errs = []
        for i in quasi:
            gb, gg = tilt_from_gravity(sign * samples[i][GX], sign * samples[i][GY], sign * samples[i][GZ])
            errs.append(max(abs(_angdiff(gb, betas[i])), abs(_angdiff(gg, gammas[i]))))
        if errs:
            err = _median(errs)
            if err < best_err:
                best_err, best_sign = err, sign
    m["tiltErrDeg"] = round(best_err, 2) if math.isfinite(best_err) else None
    m["gravitySign"] = best_sign
    if len(quasi) < max(10, n // 10) or best_err > TILT_ERROR_MAX_DEG:
        reasons.append("tilt")

    # gyro consistency: d(orientation)/dt co-varies with rotationRate (scale-free, unit/sign-robust) ---------
    sb, sg = _smooth(betas), _smooth(gammas)
    db, dg, wx, wy = [], [], [], []
    for i in range(1, n - 1):
        dt = (ts[i + 1] - ts[i - 1]) / 1000.0
        b_rate = _angdiff(sb[i + 1], sb[i - 1]) / dt
        g_rate = _angdiff(sg[i + 1], sg[i - 1]) / dt
        if abs(g_rate) > 400 or abs(b_rate) > 400:  # skip gimbal-lock / wrap artefacts
            continue
        db.append(b_rate)
        dg.append(g_rate)
        wx.append(samples[i][RB])  # rotationRate.beta  = rotation about device x
        wy.append(samples[i][RG])  # rotationRate.gamma = rotation about device y
    rs = []
    for rate, gyro in ((db, _smooth(wx)), (dg, _smooth(wy))):
        mean = sum(rate) / len(rate) if rate else 0.0
        spread = math.sqrt(sum((x - mean) ** 2 for x in rate) / len(rate)) if rate else 0.0
        if spread > 5.0:  # only judge axes that actually moved
            rs.append(abs(_pearson(rate, gyro)))
    m["gyroCorr"] = [round(r, 3) for r in rs]
    if not rs or min(rs) < 0.5:
        reasons.append("gyro")

    # targets, in order, each held for holdMs, relative to the user's own baseline ------------------------
    base_idx = [i for i in range(n) if ts[i] - ts[0] <= challenge["baselineMs"]]
    b0 = _median([betas[i] for i in base_idx]) if base_idx else betas[0]
    g0 = _median([gammas[i] for i in base_idx]) if base_idx else gammas[0]
    k, hold_start, reached = 0, None, []
    targets = challenge["targets"]
    start_i = base_idx[-1] + 1 if base_idx else 0
    for i in range(start_i, n):
        if k >= len(targets):
            break
        tgt = targets[k]
        d = math.hypot(_angdiff(betas[i], b0) - tgt["dBeta"], _angdiff(gammas[i], g0) - tgt["dGamma"])
        if d <= tgt["radius"] + 2.0:  # +2 deg server slack for sensor noise
            hold_start = ts[i] if hold_start is None else hold_start
            if ts[i] - hold_start >= tgt["holdMs"] * 0.8:  # 20% slack for event timing
                reached.append(round(ts[i] - ts[0]))
                k, hold_start = k + 1, None
        else:
            hold_start = None
    m["targetsReached"] = k
    m["reachedAtMs"] = reached
    if k < len(targets):
        reasons.append("targets")

    return ImuResult(passed=not reasons, reasons=reasons, metrics=m)
