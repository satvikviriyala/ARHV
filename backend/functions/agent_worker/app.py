"""Phase 1 worker stub; the Bedrock red team is implemented in the later sprint block."""

from __future__ import annotations

from typing import Any

from pact_core import log, store


def handler(event: dict[str, Any], _context: object) -> dict[str, str]:
    run_id = str(event.get("runId", ""))
    if run_id and store.get_run(run_id) is not None:
        store.update_run(run_id, status="error", error="not_implemented")
        log.log_event("agent_run_error", runId=run_id, error="not_implemented")
    return {"status": "error", "error": "not_implemented"}
