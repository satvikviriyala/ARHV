"""Motion-Defined Glyph (MDG) challenge generator - reference implementation (stdlib only).

The hidden shape exists ONLY in the relative motion of two random-dot textures:
dots inside the shape drift one way, dots outside drift (near-)opposite. Any single
frame is statistically uniform noise, so a screenshot carries no information about
the answer. Humans see the shape instantly (Gestalt "common fate").

Security notes (keep these properties when porting):
  * All randomness comes from KeyedRng (SHAKE-256 keyed by a secret 32-byte seed).
    Never use `random.Random` here: Mersenne Twister state can be reconstructed from
    the published dot coordinates, which would reveal hidden dots and hence the mask.
  * `generate_challenge()` returns {"public", "answers", "specs"}. Only "public" may
    ever leave the server. The seed and answers stay in DynamoDB.
"""

from __future__ import annotations

import base64
import hashlib
import math
import struct
from dataclasses import asdict, dataclass

FAMILY = "mdg-v1"
W = H = 160  # logical canvas size (px); the client scales it up with CSS
DOT = 2  # dot edge length (logical px)
SPAN = W - DOT + 1  # valid top-left coordinates per axis: 0..158
N_DOTS = 600  # dots per texture (~= visible dots per frame)
FRAMES = 36  # frames per round (client plays ping-pong at 30 fps)
ROUNDS = 3  # rounds per challenge; pass = all rounds correct
N_OPTIONS = 6  # options per round: 1 correct + 5 distractors (chance = 1/6 per round)
NOISE = 0.15  # fraction of dots re-drawn at random every frame (defeats dot tracking)

SHAPES = ("circle", "square", "triangle", "star", "plus", "heart", "arrow", "moon")
DIRS = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))  # px/frame


class KeyedRng:
    """Deterministic CSPRNG: SHAKE-256(key | label | counter). Unpredictable without the key."""

    def __init__(self, key: bytes, label: str) -> None:
        self._prefix = key + b"|" + label.encode() + b"|"
        self._counter = 0
        self._buf = b""
        self._pos = 0

    def _take(self, n: int) -> bytes:
        if self._pos + n > len(self._buf):
            self._buf = self._buf[self._pos :] + hashlib.shake_256(
                self._prefix + self._counter.to_bytes(8, "big")
            ).digest(16384)
            self._counter += 1
            self._pos = 0
        out = self._buf[self._pos : self._pos + n]
        self._pos += n
        return out

    def randbelow(self, n: int) -> int:
        """Unbiased integer in [0, n) via rejection sampling on 32-bit words."""
        limit = (1 << 32) - ((1 << 32) % n)
        while True:
            v = int.from_bytes(self._take(4), "big")
            if v < limit:
                return v % n

    def random(self) -> float:
        return int.from_bytes(self._take(7), "big") / float(1 << 56)

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self.random()

    def choice(self, seq):
        return seq[self.randbelow(len(seq))]

    def shuffle(self, items: list) -> None:
        for i in range(len(items) - 1, 0, -1):
            j = self.randbelow(i + 1)
            items[i], items[j] = items[j], items[i]

    def sample(self, seq, k: int) -> list:
        pool = list(seq)
        self.shuffle(pool)
        return pool[:k]


# ---------------------------------------------------------------- shapes
def _pip(u: float, v: float, poly) -> bool:
    inside, j = False, len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > v) != (yj > v) and u < (xj - xi) * (v - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


_TRIANGLE = ((0.0, -0.95), (0.9, 0.7), (-0.9, 0.7))
_STAR = tuple(
    (
        (0.98 if k % 2 == 0 else 0.42) * math.cos(-math.pi / 2 + k * math.pi / 5),
        (0.98 if k % 2 == 0 else 0.42) * math.sin(-math.pi / 2 + k * math.pi / 5),
    )
    for k in range(10)
)
_ARROW = ((-0.9, -0.24), (0.1, -0.24), (0.1, -0.62), (0.95, 0.0), (0.1, 0.62), (0.1, 0.24), (-0.9, 0.24))


def inside_shape(shape: str, u: float, v: float) -> bool:
    """Shape-local coords (u, v) in [-1, 1]; +v points DOWN (canvas convention)."""
    if shape == "circle":
        return u * u + v * v <= 0.82 * 0.82
    if shape == "square":
        return abs(u) <= 0.72 and abs(v) <= 0.72
    if shape == "triangle":
        return _pip(u, v, _TRIANGLE)
    if shape == "star":
        return _pip(u, v, _STAR)
    if shape == "plus":
        return (abs(u) <= 0.3 and abs(v) <= 0.9) or (abs(v) <= 0.3 and abs(u) <= 0.9)
    if shape == "heart":
        x, y = u * 1.25, -(v * 1.25) + 0.25
        return (x * x + y * y - 1) ** 3 - x * x * y**3 <= 0
    if shape == "arrow":
        return _pip(u, v, _ARROW)
    if shape == "moon":
        return u * u + v * v <= 0.85 * 0.85 and (u - 0.42) ** 2 + (v + 0.12) ** 2 > 0.66 * 0.66
    raise ValueError(f"unknown shape {shape!r}")


@dataclass(frozen=True)
class RoundSpec:
    shape: str
    cx: float
    cy: float
    radius: float
    rot: float  # radians
    fig_v: tuple[int, int]  # figure texture velocity (px/frame)
    gnd_v: tuple[int, int]  # ground texture velocity (px/frame)
    options: tuple[str, ...]


def make_round_spec(rng: KeyedRng) -> RoundSpec:
    shape = rng.choice(SHAPES)
    rot = math.radians(rng.uniform(-25.0, 25.0))
    if shape == "arrow":
        rot += rng.choice((0.0, math.pi / 2, math.pi, 3 * math.pi / 2))
    fi = rng.randbelow(8)
    gi = (fi + 4 + rng.choice((-1, 0, 1))) % 8  # ground drifts (near-)opposite
    options = [shape, *rng.sample([s for s in SHAPES if s != shape], N_OPTIONS - 1)]
    rng.shuffle(options)
    return RoundSpec(
        shape=shape,
        cx=W / 2 + rng.uniform(-12, 12),
        cy=H / 2 + rng.uniform(-12, 12),
        radius=rng.uniform(46, 56),
        rot=rot,
        fig_v=DIRS[fi],
        gnd_v=DIRS[gi],
        options=tuple(options),
    )


def make_mask(spec: RoundSpec) -> bytearray:
    """mask[y * W + x] == 1 iff a dot whose top-left is (x, y) belongs to the figure."""
    c, s = math.cos(-spec.rot), math.sin(-spec.rot)
    mask = bytearray(W * H)
    for y in range(SPAN):
        for x in range(SPAN):
            dx = (x + DOT / 2 - spec.cx) / spec.radius
            dy = (y + DOT / 2 - spec.cy) / spec.radius
            u, v = dx * c - dy * s, dx * s + dy * c
            if -1.2 <= u <= 1.2 and -1.2 <= v <= 1.2 and inside_shape(spec.shape, u, v):
                mask[y * W + x] = 1
    return mask


def render_round(spec: RoundSpec, tex: KeyedRng, noise: KeyedRng, frames: int = FRAMES):
    """List of frames; each frame is a shuffled list of (x, y) dot top-left positions."""
    mask = make_mask(spec)
    n_coh = int(N_DOTS * (1 - NOISE))
    n_noise = N_DOTS - n_coh
    fig = [(tex.randbelow(SPAN), tex.randbelow(SPAN)) for _ in range(n_coh)]
    gnd = [(tex.randbelow(SPAN), tex.randbelow(SPAN)) for _ in range(n_coh)]
    out = []
    for t in range(frames):
        fx, fy = spec.fig_v[0] * t, spec.fig_v[1] * t
        gx, gy = spec.gnd_v[0] * t, spec.gnd_v[1] * t
        pts = []
        for x0, y0 in fig:
            x, y = (x0 + fx) % SPAN, (y0 + fy) % SPAN
            if mask[y * W + x]:
                pts.append((x, y))
        for x0, y0 in gnd:
            x, y = (x0 + gx) % SPAN, (y0 + gy) % SPAN
            if not mask[y * W + x]:
                pts.append((x, y))
        pts.extend((noise.randbelow(SPAN), noise.randbelow(SPAN)) for _ in range(n_noise))
        noise.shuffle(pts)  # dot order carries no identity
        out.append(pts)
    return out


# ---------------------------------------------------------------- wire format
def encode_frames(frames) -> str:
    """Per frame: [uint16 big-endian count][count x (uint8 x, uint8 y)]; whole round base64."""
    buf = bytearray()
    for pts in frames:
        buf += struct.pack(">H", len(pts))
        for x, y in pts:
            buf.append(x)
            buf.append(y)
    return base64.b64encode(bytes(buf)).decode("ascii")


def decode_frames(b64: str):
    raw, i, frames = base64.b64decode(b64), 0, []
    while i < len(raw):
        (n,) = struct.unpack_from(">H", raw, i)
        i += 2
        frames.append([(raw[i + 2 * k], raw[i + 2 * k + 1]) for k in range(n)])
        i += 2 * n
    return frames


# ---------------------------------------------------------------- challenge
def generate_challenge(seed: bytes, rounds: int = ROUNDS, frames: int = FRAMES) -> dict:
    """seed: 32 secret bytes (secrets.token_bytes(32)). Deterministic for a given seed."""
    if len(seed) < 16:
        raise ValueError("seed must be >= 16 random bytes")
    spec_rng, tex_rng, noise_rng = KeyedRng(seed, "spec"), KeyedRng(seed, "tex"), KeyedRng(seed, "noise")
    public_rounds, answers, specs = [], [], []
    for _ in range(rounds):
        spec = make_round_spec(spec_rng)
        fr = render_round(spec, tex_rng, noise_rng, frames)
        public_rounds.append({"frames": encode_frames(fr), "frameCount": len(fr), "options": list(spec.options)})
        answers.append(spec.shape)
        specs.append(asdict(spec))
    public = {
        "family": FAMILY,
        "width": W,
        "height": H,
        "dot": DOT,
        "fps": 30,
        "playback": "pingpong",
        "rounds": public_rounds,
    }
    return {"public": public, "answers": answers, "specs": specs}


def check_answers(expected: list[str], submitted: list[str]) -> tuple[bool, int]:
    """Returns (passed, rounds_correct). Pass requires every round correct."""
    if not isinstance(submitted, list) or len(submitted) != len(expected):
        return False, 0
    correct = sum(1 for e, s in zip(expected, submitted, strict=True) if isinstance(s, str) and s == e)
    return correct == len(expected), correct
