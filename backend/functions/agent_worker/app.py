"""Asynchronous Strands/Bedrock red-team worker.

The API Lambda only queues a run. This function owns model calls, artifact uploads,
scoring, and the run lifecycle so an HTTP request never waits for Bedrock.
"""

from __future__ import annotations

import os
import secrets
import time
from functools import lru_cache
from typing import Any

import boto3
from pact_agent import models, solver
from pact_core import config, ids, log, mdg, png, store


@lru_cache(maxsize=1)
def _s3_client():
    return boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))


def _now() -> int:
    return int(time.time())


def _set_error(run_id: str, message: str, *, rounds: list[dict[str, Any]] | None = None) -> dict[str, str]:
    fields: dict[str, Any] = {
        "status": "error",
        "error": message,
        "finishedAt": _now(),
    }
    if rounds is not None:
        fields["rounds"] = rounds
    try:
        store.update_run(run_id, **fields)
    except Exception:
        log.get_logger().exception("agent_run_error_update_failed", extra={"runId": run_id})
    log.log_event("agent_run_error", runId=run_id, error=message)
    return {"status": "error", "error": message}


def _upload_frames(run_id: str, round_index: int, frames: list[list[tuple[int, int]]]) -> list[str]:
    bucket = os.environ["ARTIFACTS_BUCKET"]
    keys: list[str] = []
    for frame_index, frame in enumerate(frames):
        key = f"runs/{run_id}/r{round_index}_f{frame_index}.png"
        _s3_client().put_object(
            Bucket=bucket,
            Key=key,
            Body=png.render_frame_png(frame, scale=3),
            ContentType="image/png",
        )
        keys.append(key)
    return keys


def handler(event: dict[str, Any], _context: object) -> dict[str, Any]:
    run_id = str(event.get("runId", ""))
    if not run_id:
        return {"status": "ignored"}

    run = store.get_run(run_id)
    if not run or run.get("status") != "queued":
        return {"status": "ignored"}

    store.update_run(run_id, status="running", startedAt=_now(), progress=0)
    rounds: list[dict[str, Any]] = []
    try:
        alias = str(run["model"])
        frame_count = int(run["frames"])
        model = models.build_model("bedrock", alias)
        now = _now()
        seed = secrets.token_bytes(32)
        challenge_id = ids.new_id("ch")
        generated = mdg.generate_challenge(seed)
        cohort = f"agent:{alias}:k{frame_count}"
        store.put_challenge(
            challenge_id,
            seed_hex=seed.hex(),
            cohort=cohort,
            family=mdg.FAMILY,
            now=now,
            expires_at=now + config.CHALLENGE_TTL_S,
            answers=generated["answers"],
        )
        store.update_run(run_id, challengeId=challenge_id)

        for round_index, round_data in enumerate(generated["public"]["rounds"]):
            frames = mdg.decode_frames(round_data["frames"])[:frame_count]
            frame_keys = _upload_frames(run_id, round_index, frames)
            attempt = solver.solve_round(
                model, [png.render_frame_png(frame, scale=3) for frame in frames], round_data["options"]
            )
            round_result: dict[str, Any] = {
                "index": round_index,
                "options": list(round_data["options"]),
                "frameKeys": frame_keys,
                "answer": attempt.answer,
                "confidence": attempt.confidence,
                "rationale": attempt.rationale,
                "valid": attempt.valid,
                "latencyMs": attempt.latency_ms,
                "repaired": attempt.repaired,
                "error": attempt.error,
            }
            rounds.append(round_result)
            store.update_run(run_id, rounds=rounds, progress=round_index + 1)
            log.log_event(
                "agent_round",
                runId=run_id,
                roundIndex=round_index,
                valid=attempt.valid,
                repaired=attempt.repaired,
                error=attempt.error,
            )
            if attempt.error:
                return _set_error(f"{run_id}", f"model_error: {attempt.error}", rounds=rounds)

        record = store.consume_challenge(challenge_id, now=_now())
        answers = [str(round_result.get("answer") or "") for round_result in rounds]
        passed, correct = mdg.check_answers(record["answers"], answers)
        for index, round_result in enumerate(rounds):
            truth = str(record["answers"][index])
            round_result["truth"] = truth
            round_result["correct"] = round_result.get("answer") == truth
        finished_at = _now()
        store.record_attempt(
            cohort=cohort,
            family=mdg.FAMILY,
            passed=passed,
            rounds_correct=correct,
            rounds_total=mdg.ROUNDS,
            duration_ms=sum(int(round_result["latencyMs"]) for round_result in rounds),
            now=finished_at,
        )
        store.update_run(
            run_id,
            status="done",
            progress=mdg.ROUNDS,
            rounds=rounds,
            passed=passed,
            roundsCorrect=correct,
            finishedAt=finished_at,
            error=None,
        )
        log.log_event("agent_run_done", runId=run_id, passed=passed, roundsCorrect=correct)
        return {"status": "done", "passed": passed, "roundsCorrect": correct}
    except Exception as exc:
        return _set_error(run_id, f"worker_error: {type(exc).__name__}", rounds=rounds)
