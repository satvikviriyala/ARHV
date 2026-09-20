"""Red-team the physical (imu-v1) challenge: what cheap bots send vs. what a physics-aware simulator sends.

Offline (no AWS; Build It):   python scripts/imu_attack_demo.py
Against the deployed API:     python scripts/imu_attack_demo.py --api https://<id>.execute-api.us-east-1.amazonaws.com

Expected: orientation-only, dead-gyro, mismatched-gravity, teleporting and replayed traces are REJECTED;
the physics-consistent synthetic trace PASSES. That last line is the argument for vendor-attested sensors:
over an unattested web channel, a good simulator is indistinguishable from a phone (docs/PHYSICAL.md).
"""

import argparse
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend", "layers", "core"))
sys.path.insert(0, ROOT)
import secrets  # noqa: E402

from pact_core import imu  # noqa: E402

from redteam import imu_sim  # noqa: E402


def _post(url: str, body: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        method="POST",
        headers={"content-type": "application/json", "x-pact-cohort": "agent:imu-sim:k0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--api", default=None, help="deployed API base URL; omit to run the verifier offline")
    a = p.parse_args()

    def fresh():
        if a.api:
            ch = _post(f"{a.api}/v1/challenges", {"family": "imu-v1"})
            return ch, ch["challengeId"]
        return imu.generate_challenge(secrets.token_bytes(32)), "ch_" + secrets.token_hex(12)

    def submit(ch, cid, trace):
        if a.api:
            r = _post(f"{a.api}/v1/challenges/{cid}/answers", {"trace": trace})
            return r.get("passed", False), r.get("reasons", [])
        res = imu.verify(ch, cid, trace)
        return res.passed, res.reasons

    other, other_id = fresh()
    recording = imu_sim.physical_trace(other, other_id, seed=11)  # a genuine-looking earlier session
    attacks = [
        (
            "orientation-only spoof (DevTools-style)",
            lambda ch, cid: imu_sim.orientation_only_spoof(imu_sim.physical_trace(ch, cid)),
        ),
        ("dead gyroscope", lambda ch, cid: imu_sim.no_gyro_spoof(imu_sim.physical_trace(ch, cid))),
        (
            "gravity from a phone lying on a desk",
            lambda ch, cid: imu_sim.mismatched_gravity_spoof(imu_sim.physical_trace(ch, cid)),
        ),
        ("teleporting scripted bot", lambda ch, cid: imu_sim.teleport_spoof(ch, cid)),
        (
            "replayed recording (re-bound to new id)",
            lambda ch, cid: dict(recording, challengeId=cid, nonce=ch["nonce"]),
        ),
        ("physics-consistent simulator (no phone)", lambda ch, cid: imu_sim.physical_trace(ch, cid, seed=99)),
    ]
    print(f"{'attack':44} result    failed checks")
    print("-" * 80)
    for name, make in attacks:
        ch, cid = fresh()
        passed, reasons = submit(ch, cid, make(ch, cid))
        print(f"{name:44} {'PASSED' if passed else 'REJECTED':9} {', '.join(reasons) or '-'}")
    print("-" * 80)
    print("The last row is the point: without vendor attestation of the sensor stream, physics alone can be faked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
