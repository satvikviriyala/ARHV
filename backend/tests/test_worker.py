from conftest import load_handler
from pact_core import store


def test_phase_one_worker_marks_existing_run_not_implemented(ddb_table):
    worker = load_handler("agent_worker")
    run_id = "run_" + "a" * 24
    store.create_run({"runId": run_id, "status": "queued", "ttl": 1})
    result = worker.handler({"runId": run_id}, None)
    assert result["error"] == "not_implemented"
    assert store.get_run(run_id)["status"] == "error"
