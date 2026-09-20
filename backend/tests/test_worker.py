import boto3
from conftest import load_handler
from pact_agent import models
from pact_core import store
from test_agent import FakeModel


def _run(run_id: str, *, frames: int = 4) -> dict:
    return {
        "runId": run_id,
        "status": "queued",
        "model": "nova-2-lite",
        "modelId": "us.amazon.nova-2-lite-v1:0",
        "frames": frames,
        "progress": 0,
        "rounds": [],
        "passed": False,
        "roundsCorrect": 0,
        "error": None,
        "createdAt": 1_700_000_000,
        "ttl": 1_700_000_000 + 604_800,
    }


def _create_bucket():
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="agent-artifacts")


def test_worker_runs_fake_model_uploads_frames_and_records_stats(ddb_table, monkeypatch):
    del ddb_table
    monkeypatch.setenv("ARTIFACTS_BUCKET", "agent-artifacts")
    monkeypatch.setenv("AGENT_MODELS", "nova-2-lite=us.amazon.nova-2-lite-v1:0")
    _create_bucket()
    worker = load_handler("agent_worker")
    worker._s3_client.cache_clear()
    run_id = "run_" + "a" * 24
    store.create_run(_run(run_id))
    statuses: list[str] = []
    original_update = worker.store.update_run

    def capture_update(target: str, **fields):
        if "status" in fields:
            statuses.append(str(fields["status"]))
        return original_update(target, **fields)

    monkeypatch.setattr(worker.store, "update_run", capture_update)
    monkeypatch.setattr(
        models,
        "build_model",
        lambda *args, **kwargs: FakeModel(['{"answer":"circle","confidence":0.3}'] * 6),
    )

    result = worker.handler({"runId": run_id}, None)

    assert result["status"] == "done"
    run = store.get_run(run_id)
    assert run["status"] == "done"
    assert statuses == ["running", "done"]
    assert run["challengeId"].startswith("ch_")
    assert len(run["rounds"]) == 3
    assert all(len(round_result["frameKeys"]) == 4 for round_result in run["rounds"])
    assert all("truth" in round_result and "correct" in round_result for round_result in run["rounds"])
    objects = boto3.client("s3", region_name="us-east-1").list_objects_v2(Bucket="agent-artifacts")["Contents"]
    assert len(objects) == 12
    item = next(item for item in store.get_stats("mdg-v1") if item["cohort"] == "agent:nova-2-lite:k4")
    assert item["attempts"] == 1 and item["roundsTotal"] == 3


def test_worker_labels_model_failure_as_infrastructure_and_skips_stats(ddb_table, monkeypatch):
    del ddb_table
    monkeypatch.setenv("ARTIFACTS_BUCKET", "agent-artifacts")
    _create_bucket()
    worker = load_handler("agent_worker")
    worker._s3_client.cache_clear()
    run_id = "run_" + "b" * 24
    store.create_run(_run(run_id, frames=1))
    monkeypatch.setattr(models, "build_model", lambda *args, **kwargs: FakeModel([]))

    result = worker.handler({"runId": run_id}, None)

    assert result["status"] == "error"
    assert result["error"].startswith("model_error:")
    run = store.get_run(run_id)
    assert run["status"] == "error"
    assert run["error"].startswith("model_error:")
    assert store.get_stats("mdg-v1") == []
