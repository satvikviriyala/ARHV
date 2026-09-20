import json
import os
import sys

import boto3
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


class FakeLambdaClient:
    def __init__(self):
        self.calls: list[dict] = []

    def invoke(self, **kwargs):
        self.calls.append(kwargs)
        return {"StatusCode": 202}


def test_agent_run_api_queues_event_and_polls_queued_run(ddb_table, monkeypatch):
    api = load_handler("api")
    monkeypatch.setenv("AGENT_MODELS", "nova-2-lite=us.amazon.nova-2-lite-v1:0")
    monkeypatch.setenv("WORKER_FUNCTION_NAME", "pact-dev-AgentWorkerFunction")
    fake_lambda = FakeLambdaClient()
    api._lambda_client.cache_clear()
    monkeypatch.setattr(api, "_lambda_client", lambda: fake_lambda)

    status, queued = unpack(api.handler(event("POST", "/v1/agent-runs", {"model": "nova-2-lite", "frames": 4}), None))

    assert status == 202
    assert queued["status"] == "queued" and queued["runId"].startswith("run_")
    assert fake_lambda.calls[0]["InvocationType"] == "Event"
    assert json.loads(fake_lambda.calls[0]["Payload"]) == {"runId": queued["runId"]}
    status, polled = unpack(api.handler(event("GET", f"/v1/agent-runs/{queued['runId']}"), None))
    assert status == 200 and polled["status"] == "queued" and polled["rounds"] == []


def test_agent_run_api_validates_model_frames_local_fallback_and_daily_cap(ddb_table, monkeypatch):
    api = load_handler("api")
    monkeypatch.setenv("AGENT_MODELS", "nova-2-lite=us.amazon.nova-2-lite-v1:0")
    monkeypatch.setenv("WORKER_FUNCTION_NAME", "worker")
    fake_lambda = FakeLambdaClient()
    monkeypatch.setattr(api, "_lambda_client", lambda: fake_lambda)
    monkeypatch.setenv("AGENT_RUNS_DAILY_CAP", "1")

    status, body = unpack(api.handler(event("POST", "/v1/agent-runs", {"model": "unknown"}), None))
    assert status == 400 and body["error"]["code"] == "bad_model"
    status, body = unpack(api.handler(event("POST", "/v1/agent-runs", {"frames": 2}), None))
    assert status == 400 and body["error"]["code"] == "bad_frames"
    status, _ = unpack(api.handler(event("POST", "/v1/agent-runs", {"frames": 1}), None))
    assert status == 202
    status, body = unpack(api.handler(event("POST", "/v1/agent-runs", {"frames": 1}), None))
    assert status == 429 and body["error"]["code"] == "daily_cap"
    monkeypatch.setattr(api.config, "LOCAL_DEV", True)
    status, body = unpack(api.handler(event("POST", "/v1/agent-runs", {}), None))
    assert status == 501 and body["error"]["code"] == "cloud_only"


def test_get_agent_run_presigns_frames_and_replay_only_when_done(ddb_table, monkeypatch):
    del ddb_table
    api = load_handler("api")
    monkeypatch.setenv("ARTIFACTS_BUCKET", "agent-artifacts")
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="agent-artifacts")
    s3.put_object(Bucket="agent-artifacts", Key="runs/run_" + "c" * 24 + "/r0_f0.png", Body=b"\x89PNG")
    run_id = "run_" + "c" * 24
    challenge_id = "ch_" + "d" * 24
    store.put_challenge(
        challenge_id,
        seed_hex="ab" * 32,
        cohort="agent:nova-2-lite:k1",
        family="mdg-v1",
        now=1_700_000_000,
        expires_at=1_700_000_180,
        answers=["circle", "star", "heart"],
    )
    store.create_run(
        {
            "runId": run_id,
            "status": "done",
            "model": "nova-2-lite",
            "modelId": "us.amazon.nova-2-lite-v1:0",
            "frames": 1,
            "progress": 3,
            "challengeId": challenge_id,
            "rounds": [
                {
                    "index": 0,
                    "options": ["circle"],
                    "frameKeys": [f"runs/{run_id}/r0_f0.png"],
                    "answer": "circle",
                    "truth": "circle",
                    "correct": True,
                }
            ],
            "passed": True,
            "roundsCorrect": 3,
            "error": None,
            "createdAt": 1_700_000_000,
            "finishedAt": 1_700_000_010,
            "ttl": 1_700_000_000 + 604_800,
        }
    )
    api._s3_client.cache_clear()

    status, without_replay = unpack(api.handler(event("GET", f"/v1/agent-runs/{run_id}"), None))
    assert status == 200
    assert "replay" not in without_replay
    assert "frameKeys" not in without_replay["rounds"][0]
    assert without_replay["rounds"][0]["frameUrls"][0].startswith("https://")
    status, with_replay = unpack(
        api.handler(
            {
                "requestContext": {"http": {"method": "GET", "rawPath": f"/v1/agent-runs/{run_id}"}},
                "queryStringParameters": {"replay": "1"},
            },
            None,
        )
    )
    assert status == 200 and "replay" in with_replay
    assert all(key not in json.dumps(with_replay["replay"]) for key in ("answers", "seedHex", "specs"))
