import math
import os
import secrets
import sys

import pytest
from pact_core import imu

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from redteam import imu_sim  # noqa: E402


def _challenge():
    return imu.generate_challenge(secrets.token_bytes(32)), "ch_" + secrets.token_hex(12)


def test_challenge_is_fresh_and_well_formed():
    a, b = imu.generate_challenge(bytes(32)), imu.generate_challenge(bytes(32))
    assert a == b  # deterministic per seed
    c, _ = _challenge()
    assert c["nonce"] != a["nonce"] and len(c["nonce"]) == 32
    assert len(c["targets"]) == imu.N_TARGETS
    for t in c["targets"]:
        mag = (t["dBeta"] ** 2 + t["dGamma"] ** 2) ** 0.5
        assert imu.TARGET_TILT[0] - 0.2 <= mag <= imu.TARGET_TILT[1] + 0.2
    for t1, t2 in zip(c["targets"], c["targets"][1:], strict=False):
        assert (t1["dBeta"], t1["dGamma"]) != (t2["dBeta"], t2["dGamma"])


@pytest.mark.parametrize("ios", [False, True])
@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_physically_consistent_trace_passes(ios, seed):
    """A coherent motion trace passes on both the Android and the iOS gravity sign convention."""
    ch, cid = _challenge()
    res = imu.verify(ch, cid, imu_sim.physical_trace(ch, cid, ios=ios, seed=seed))
    assert res.passed, (res.reasons, res.metrics)
    assert res.metrics["targetsReached"] == imu.N_TARGETS
    assert res.metrics["gravitySign"] == (-1 if ios else 1)


def test_wrong_nonce_or_challenge_is_rejected():
    ch, cid = _challenge()
    tr = imu_sim.physical_trace(ch, cid)
    assert imu.verify(ch, cid, dict(tr, nonce="00" * 16)).reasons == ["binding"]
    assert imu.verify(ch, "ch_other", tr).reasons == ["binding"]


def test_replayed_recording_fails_on_fresh_targets():
    """A genuine recording from challenge A is useless for challenge B: different targets (and nonce)."""
    a, aid = _challenge()
    b, bid = _challenge()
    rec = imu_sim.physical_trace(a, aid)
    forged = dict(rec, challengeId=bid, nonce=b["nonce"])  # attacker even fixes the binding fields
    res = imu.verify(b, bid, forged)
    assert not res.passed and "targets" in res.reasons


def test_orientation_only_spoof_is_rejected():
    ch, cid = _challenge()
    res = imu.verify(ch, cid, imu_sim.orientation_only_spoof(imu_sim.physical_trace(ch, cid)))
    assert not res.passed and "gravity" in res.reasons


def test_dead_gyro_spoof_is_rejected():
    ch, cid = _challenge()
    res = imu.verify(ch, cid, imu_sim.no_gyro_spoof(imu_sim.physical_trace(ch, cid)))
    assert not res.passed and "gyro" in res.reasons


def test_gravity_inconsistent_with_orientation_is_rejected():
    ch, cid = _challenge()
    res = imu.verify(ch, cid, imu_sim.mismatched_gravity_spoof(imu_sim.physical_trace(ch, cid)))
    assert not res.passed and "tilt" in res.reasons


def test_teleporting_bot_is_rejected():
    ch, cid = _challenge()
    res = imu.verify(ch, cid, imu_sim.teleport_spoof(ch, cid))
    assert not res.passed and "continuity" in res.reasons


def test_timing_and_size_limits():
    ch, cid = _challenge()
    tr = imu_sim.physical_trace(ch, cid)
    fast = dict(tr, samples=[[s[0] / 20] + s[1:] for s in tr["samples"]])  # 20x too fast
    assert "timing" in imu.verify(ch, cid, fast).reasons
    back = dict(tr, samples=list(reversed(tr["samples"])))
    assert imu.verify(ch, cid, back).reasons == ["timing"]
    assert imu.verify(ch, cid, dict(tr, samples=tr["samples"][:10])).reasons == ["size"]
    bad = dict(tr, samples=[s[:9] for s in tr["samples"]])
    assert imu.verify(ch, cid, bad).reasons == ["format"]


def test_targets_out_of_order_fail():
    ch, cid = _challenge()
    swapped = dict(ch, targets=list(reversed(ch["targets"])))
    tr = imu_sim.physical_trace(swapped, cid)  # visits targets in reverse order
    res = imu.verify(ch, cid, tr)
    assert not res.passed and "targets" in res.reasons


def test_physically_consistent_synthetic_trace_passes_documenting_the_attestation_gap():
    """Honest limit: a simulator that models the physics passes, because the web channel is unattested.
    This is exactly why ARHV argues for vendor-attested sensor streams (docs/PHYSICAL.md)."""
    ch, cid = _challenge()
    synthetic = imu_sim.physical_trace(ch, cid, seed=99)  # no phone involved at all
    assert imu.verify(ch, cid, synthetic).passed


def test_demo_tilt_tolerance_handles_fusion_bias_but_not_cheap_spoofs():
    """A modest browser fusion/calibration offset is human-like; independent spoof signals still fail."""
    ch, cid = _challenge()
    trace = imu_sim.physical_trace(ch, cid, seed=11)
    fusion_biased = dict(trace, samples=[[s[0], s[1] + 14.0, *s[2:]] for s in trace["samples"]])

    human_like = imu.verify(ch, cid, fusion_biased)
    assert human_like.passed, (human_like.reasons, human_like.metrics)
    assert 12.0 < human_like.metrics["tiltErrDeg"] <= imu.TILT_ERROR_MAX_DEG

    for spoof in (
        imu_sim.orientation_only_spoof(trace),
        imu_sim.no_gyro_spoof(trace),
        imu_sim.mismatched_gravity_spoof(trace),
    ):
        result = imu.verify(ch, cid, spoof)
        assert not result.passed


def test_noisy_low_rate_mobile_trace_passes_with_documented_limits():
    """A lower-rate browser stream with modest fusion noise remains a coherent physical proof."""
    ch, cid = _challenge()
    trace = imu_sim.physical_trace(ch, cid, seed=23)
    samples = []
    for i, sample in enumerate(trace["samples"][::9]):
        row = list(sample)
        row[0] = i * 150.0
        row[1] += 1.5 * math.sin(i * 0.7)
        row[2] += 1.5 * math.cos(i * 0.53)
        samples.append(row)

    result = imu.verify(ch, cid, dict(trace, samples=samples))
    assert result.passed, (result.reasons, result.metrics)
    assert result.metrics["medianDtMs"] == 150.0
    assert result.metrics["tiltErrDeg"] < imu.TILT_ERROR_MAX_DEG
    assert result.metrics["targetsReached"] == imu.N_TARGETS


def test_tilt_from_gravity_matches_convention():
    import math

    for beta, gamma in [(0, 0), (30, 0), (45, 20), (60, -25), (-20, 10)]:
        b, g = math.radians(beta), math.radians(gamma)
        gx, gy, gz = -9.81 * math.cos(b) * math.sin(g), 9.81 * math.sin(b), 9.81 * math.cos(b) * math.cos(g)
        rb, rg = imu.tilt_from_gravity(gx, gy, gz)
        assert abs(rb - beta) < 1e-6 and abs(rg - gamma) < 1e-6
