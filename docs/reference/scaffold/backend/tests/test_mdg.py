import json
import math
import secrets
import struct
import time

from pact_core import mdg, png


def test_deterministic_for_same_seed_and_different_for_new_seed():
    seed = bytes(range(32))
    a, b = mdg.generate_challenge(seed), mdg.generate_challenge(seed)
    assert a["public"] == b["public"] and a["answers"] == b["answers"]
    assert mdg.generate_challenge(secrets.token_bytes(32))["public"] != a["public"]


def test_public_payload_never_contains_answers_or_specs():
    ch = mdg.generate_challenge(secrets.token_bytes(32))
    blob = json.dumps(ch["public"])
    for key in ("answers", "answer", "shape", "specs", "fig_v", "gnd_v", "seed", "mask"):
        assert f'"{key}"' not in blob
    for r, ans in zip(ch["public"]["rounds"], ch["answers"], strict=True):
        assert ans in r["options"] and len(set(r["options"])) == mdg.N_OPTIONS


def test_encoding_roundtrip():
    seed = secrets.token_bytes(32)
    spec = mdg.make_round_spec(mdg.KeyedRng(seed, "spec"))
    frames = mdg.render_round(spec, mdg.KeyedRng(seed, "tex"), mdg.KeyedRng(seed, "noise"), frames=5)
    assert mdg.decode_frames(mdg.encode_frames(frames)) == frames


def test_single_frame_carries_no_shape_signal():
    """Dot density inside the (secret) mask must match its area, i.e. a still frame is uniform noise."""
    zs = []
    for _ in range(60):
        seed = secrets.token_bytes(32)
        spec = mdg.make_round_spec(mdg.KeyedRng(seed, "spec"))
        mask = mdg.make_mask(spec)
        area = sum(mask[y * mdg.W + x] for y in range(mdg.SPAN) for x in range(mdg.SPAN)) / (mdg.SPAN**2)
        for pts in mdg.render_round(spec, mdg.KeyedRng(seed, "tex"), mdg.KeyedRng(seed, "noise"), frames=3):
            n = len(pts)
            k = sum(mask[y * mdg.W + x] for x, y in pts)
            zs.append((k - n * area) / math.sqrt(n * area * (1 - area)))
    mean = sum(zs) / len(zs)
    assert abs(mean) < 0.25, mean  # no systematic density difference
    assert max(abs(z) for z in zs) < 4.5  # no single frame is an outlier


def test_motion_reveals_the_shape():
    """Dots that move with the figure velocity between frames sit inside the mask (the human signal)."""
    seed = secrets.token_bytes(32)
    spec = mdg.make_round_spec(mdg.KeyedRng(seed, "spec"))
    mask = mdg.make_mask(spec)
    frames = mdg.render_round(spec, mdg.KeyedRng(seed, "tex"), mdg.KeyedRng(seed, "noise"), frames=8)
    inside = total = 0
    for t in range(len(frames) - 1):
        nxt = set(frames[t + 1])
        for x, y in frames[t]:
            nx, ny = (x + spec.fig_v[0]) % mdg.SPAN, (y + spec.fig_v[1]) % mdg.SPAN
            if (nx, ny) in nxt:
                total += 1
                inside += mask[y * mdg.W + x]
    assert total > 200 and inside / total > 0.75


def test_check_answers():
    assert mdg.check_answers(["a", "b", "c"], ["a", "b", "c"]) == (True, 3)
    assert mdg.check_answers(["a", "b", "c"], ["a", "x", "c"]) == (False, 2)
    assert mdg.check_answers(["a", "b", "c"], ["a", "b"]) == (False, 0)
    assert mdg.check_answers(["a", "b", "c"], "abc") == (False, 0)


def test_generation_is_fast_enough_for_lambda():
    t = time.perf_counter()
    mdg.generate_challenge(secrets.token_bytes(32))
    assert time.perf_counter() - t < 2.0


def test_png_encoder_produces_valid_png():
    seed = secrets.token_bytes(32)
    spec = mdg.make_round_spec(mdg.KeyedRng(seed, "spec"))
    pts = mdg.render_round(spec, mdg.KeyedRng(seed, "tex"), mdg.KeyedRng(seed, "noise"), frames=1)[0]
    data = png.render_frame_png(pts, scale=3)
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    w, h = struct.unpack(">II", data[16:24])
    assert (w, h) == (480, 480)
