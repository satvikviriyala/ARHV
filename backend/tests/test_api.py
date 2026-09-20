import json
import os
import sys

from conftest import load_handler
from pact_core import store, tokens

from redteam import imu_sim

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def event(method: str, path: str, body: dict | None = None, *, cohort: str | None = None) -> dict:
    headers = {"content-type": "application/json"}
    if cohort:
        headers["x-pact-cohort"] = cohort
    return {
        "requestContext": {"http": {"method": method, "rawPath": path}},
        "headers": headers,
        "body": json.dumps(body) if body is not None else "",
    }


def unpack(response: dict) -> tuple[int, dict]:
    return int(response["statusCode"]), json.loads(response["body"])


def test_imu_create_answer_spoof_replay_and_stats(ddb_table):
    api = load_handler("api")
    status, challenge = unpack(api.handler(event("POST", "/v1/challenges", {"family": "imu-v1"}), None))
    assert status == 201
    assert challenge["family"] == "imu-v1"
    assert len(challenge["nonce"]) == 32 and len(challenge["targets"]) == 3
    assert "seedHex" not in json.dumps(challenge)
    trace = imu_sim.physical_trace(challenge, challenge["challengeId"])
    status, passed = unpack(
        api.handler(
            event("POST", f"/v1/challenges/{challenge['challengeId']}/answers", {"trace": trace}),
            None,
        )
    )
    assert status == 200 and passed["passed"]
    claims = tokens.verify("local-test-secret-" + "x" * 48, passed["token"])
    assert claims["asr"] == "physical" and claims["prf"] == "imu-v1"
    status, replay = unpack(
        api.handler(
            event("POST", f"/v1/challenges/{challenge['challengeId']}/answers", {"trace": trace}),
            None,
        )
    )
    assert status == 409 and replay["error"]["code"] == "already_answered"
    status, fresh = unpack(api.handler(event("POST", "/v1/challenges", {"family": "imu-v1"}), None))
    bad = imu_sim.orientation_only_spoof(imu_sim.physical_trace(fresh, fresh["challengeId"]))
    status, result = unpack(
        api.handler(event("POST", f"/v1/challenges/{fresh['challengeId']}/answers", {"trace": bad}), None)
    )
    assert status == 200 and not result["passed"] and "gravity" in result["reasons"]
    status, stats = unpack(
        api.handler(
            {
                "requestContext": {"http": {"method": "GET", "rawPath": "/v1/stats"}},
                "queryStringParameters": {"family": "imu-v1"},
            },
            None,
        )
    )
    assert status == 200 and stats["family"] == "imu-v1" and stats["cohorts"][0]["attempts"] == 2


def test_mdg_payload_is_public_only_and_answers_pass(ddb_table):
    api = load_handler("api")
    status, challenge = unpack(api.handler(event("POST", "/v1/challenges", {}, cohort="study"), None))
    assert status == 201
    assert all(key not in challenge for key in ("answers", "specs", "seed", "mask"))
    record = store.table().get_item(Key={"PK": f"CH#{challenge['challengeId']}", "SK": "META"})["Item"]
    status, result = unpack(
        api.handler(
            event(
                "POST",
                f"/v1/challenges/{challenge['challengeId']}/answers",
                {"answers": record["answers"], "timingsMs": [100, 200, 300]},
            ),
            None,
        )
    )
    assert status == 200 and result["passed"] and result["assurance"] == "motion"


def test_api_rejects_bad_family_wrong_family_and_large_body(ddb_table):
    api = load_handler("api")
    status, body = unpack(api.handler(event("POST", "/v1/challenges", {"family": "x"}), None))
    assert status == 400 and body["error"]["code"] == "bad_family"
    _, mdg_challenge = unpack(api.handler(event("POST", "/v1/challenges", {}), None))
    trace = {"challengeId": mdg_challenge["challengeId"], "nonce": "00" * 16, "samples": []}
    status, body = unpack(
        api.handler(
            event("POST", f"/v1/challenges/{mdg_challenge['challengeId']}/answers", {"trace": trace}),
            None,
        )
    )
    assert status == 400 and body["error"]["code"] == "wrong_family"
    large = {
        "requestContext": {"http": {"method": "POST", "rawPath": "/v1/challenges/ch_" + "a" * 24 + "/answers"}},
        "body": "x" * 512_001,
    }
    status, body = unpack(api.handler(large, None))
    assert status == 400 and body["error"]["code"] == "too_large"
