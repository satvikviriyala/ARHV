"""Public API Lambda: challenge generation, verification, stats and async red-team runs."""

from __future__ import annotations

import base64
import binascii
import json
import os
import secrets
import time
from functools import lru_cache
from typing import Any

import boto3
from pact_core import config, http, ids, imu, keys, log, mdg, stats, store, tokens


def _now() -> int:
    return int(time.time())


@lru_cache(maxsize=1)
def _lambda_client():
    return boto3.client("lambda", region_name=os.environ.get("AWS_REGION", "us-east-1"))


@lru_cache(maxsize=1)
def _s3_client():
    return boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))


def _body_too_large(event: dict[str, Any]) -> bool:
    body = event.get("body")
    if not isinstance(body, str):
        return False
    if event.get("isBase64Encoded"):
        try:
            return len(base64.b64decode(body, validate=True)) > config.TRACE_MAX_BYTES
        except (binascii.Error, ValueError):
            return True
    return len(body.encode("utf-8")) > config.TRACE_MAX_BYTES


def _consume_error(exc: Exception) -> http.ApiError:
    if isinstance(exc, store.ChallengeNotFound):
        return http.ApiError(404, "not_found", "Challenge not found")
    if isinstance(exc, store.ChallengeExpired):
        return http.ApiError(410, "expired", "Challenge expired")
    if isinstance(exc, store.ChallengeAlreadyUsed):
        return http.ApiError(409, "already_answered", "Challenge was already answered")
    return http.ApiError(500, "internal", "Unexpected challenge error")


def create_challenge(event: dict[str, Any], _params: dict[str, str] | None = None) -> dict:
    body = http.parse_json(event)
    family = body.get("family") or mdg.FAMILY
    if family not in config.FAMILIES:
        raise http.ApiError(400, "bad_family", "Unknown challenge family")
    if body.get("handoffId") or body.get("phoneKey"):
        raise http.ApiError(501, "not_implemented", "Phone handoff is not implemented yet")
    cohort = ids.sanitize_cohort(http.header(event, "x-pact-cohort") or body.get("cohort"))
    now = _now()
    challenge_id = ids.new_id("ch")
    seed = secrets.token_bytes(32)
    expires_at = now + config.CHALLENGE_TTL_S
    if family == imu.FAMILY:
        challenge = imu.generate_challenge(seed)
        store.put_challenge(
            challenge_id,
            seed_hex=seed.hex(),
            cohort=cohort,
            family=family,
            now=now,
            expires_at=expires_at,
        )
        log.log_event("challenge_created", challengeId=challenge_id, cohort=cohort, family=family)
        return http.ok({"challengeId": challenge_id, "expiresAt": expires_at, **challenge}, 201)

    generated = mdg.generate_challenge(seed)
    store.put_challenge(
        challenge_id,
        seed_hex=seed.hex(),
        cohort=cohort,
        family=family,
        now=now,
        expires_at=expires_at,
        answers=generated["answers"],
    )
    log.log_event("challenge_created", challengeId=challenge_id, cohort=cohort, family=family)
    return http.ok({"challengeId": challenge_id, "expiresAt": expires_at, **generated["public"]}, 201)


def answer_challenge(event: dict[str, Any], params: dict[str, str]) -> dict:
    challenge_id = params.get("challengeId", "")
    if not ids.CHALLENGE_ID_RE.fullmatch(challenge_id):
        raise http.ApiError(400, "bad_request", "Malformed challenge id")
    if _body_too_large(event):
        raise http.ApiError(400, "too_large", "Request body is too large")
    body = http.parse_json(event)
    is_imu = "trace" in body
    if is_imu:
        if not isinstance(body["trace"], dict):
            raise http.ApiError(400, "bad_request", "trace must be an object")
    elif "answers" not in body:
        raise http.ApiError(400, "bad_request", "Expected answers or trace")

    now = _now()
    try:
        record = store.consume_challenge(challenge_id, now=now)
    except (store.ChallengeNotFound, store.ChallengeExpired, store.ChallengeAlreadyUsed) as exc:
        raise _consume_error(exc) from exc

    family = record.get("family")
    if is_imu and family != imu.FAMILY:
        raise http.ApiError(400, "wrong_family", "This challenge expects motion-puzzle answers")
    if not is_imu and family != mdg.FAMILY:
        raise http.ApiError(400, "wrong_family", "This challenge expects an IMU trace")

    if is_imu:
        challenge = imu.generate_challenge(bytes.fromhex(str(record["seedHex"])))
        result = imu.verify(challenge, challenge_id, body["trace"])
        metrics = result.metrics
        store.record_attempt(
            cohort=str(record["cohort"]),
            family=imu.FAMILY,
            passed=result.passed,
            rounds_correct=int(metrics.get("targetsReached", 0)),
            rounds_total=imu.N_TARGETS,
            duration_ms=int(metrics.get("durationMs", 0)),
            now=now,
        )
        log.log_event(
            "imu_verified",
            challengeId=challenge_id,
            passed=result.passed,
            reasons=result.reasons,
            metrics=metrics,
        )
        if not result.passed:
            return http.ok({"passed": False, "reasons": result.reasons, "metrics": metrics})
        token, claims = tokens.mint(
            keys.token_secret(),
            sub=ids.new_visitor(),
            assurance="physical",
            challenge_id=challenge_id,
            proof=imu.FAMILY,
            now=now,
        )
        log.log_event("token_minted", jti=claims["jti"], challengeId=challenge_id, asr=claims["asr"])
        return http.ok(
            {
                "passed": True,
                "token": token,
                "expiresIn": config.TOKEN_TTL_S,
                "assurance": "physical",
                "proof": imu.FAMILY,
                "metrics": metrics,
            }
        )

    answers = body.get("answers")
    if (
        not isinstance(answers, list)
        or len(answers) != mdg.ROUNDS
        or any(not isinstance(answer, str) or len(answer) > 16 for answer in answers)
    ):
        raise http.ApiError(400, "bad_request", "answers must be three short strings")
    timings = body.get("timingsMs", [])
    if timings is None:
        timings = []
    if not isinstance(timings, list) or any(not isinstance(value, (int, float)) for value in timings):
        raise http.ApiError(400, "bad_request", "timingsMs must be a list of numbers")
    duration = sum(max(0, min(600_000, int(value))) for value in timings)
    passed, correct = mdg.check_answers(record.get("answers", []), answers)
    store.record_attempt(
        cohort=str(record["cohort"]),
        family=mdg.FAMILY,
        passed=passed,
        rounds_correct=correct,
        rounds_total=mdg.ROUNDS,
        duration_ms=duration,
        now=now,
    )
    log.log_event("challenge_answered", challengeId=challenge_id, family=mdg.FAMILY, passed=passed)
    if not passed:
        return http.ok({"passed": False, "roundsCorrect": correct})
    token, claims = tokens.mint(
        keys.token_secret(),
        sub=ids.new_visitor(),
        assurance="motion",
        challenge_id=challenge_id,
        now=now,
    )
    log.log_event("token_minted", jti=claims["jti"], challengeId=challenge_id, asr=claims["asr"])
    return http.ok(
        {
            "passed": True,
            "roundsCorrect": correct,
            "token": token,
            "expiresIn": config.TOKEN_TTL_S,
            "assurance": "motion",
        }
    )


def get_stats(event: dict[str, Any], _params: dict[str, str] | None = None) -> dict:
    query = event.get("queryStringParameters") or {}
    family = query.get("family") or mdg.FAMILY
    if family not in config.FAMILIES:
        raise http.ApiError(400, "bad_family", "Unknown challenge family")
    chance = {"round": stats.CHANCE_ROUND, "pass": stats.CHANCE_PASS} if family == mdg.FAMILY else None
    return http.ok(
        {
            "family": family,
            "generatedAt": _now(),
            "chance": chance,
            "cohorts": stats.summarize(store.get_stats(family)),
        }
    )


def health(_event: dict[str, Any], _params: dict[str, str] | None = None) -> dict:
    return http.ok(
        {
            "ok": True,
            "stage": config.STAGE,
            "family": mdg.FAMILY,
            "families": list(config.FAMILIES),
            "agentModels": list(config.agent_aliases()),
            "cloudAgents": not config.LOCAL_DEV,
        }
    )


def start_agent_run(event: dict[str, Any], _params: dict[str, str] | None = None) -> dict:
    if config.LOCAL_DEV:
        raise http.ApiError(501, "cloud_only", "Run `make bench BACKEND=ollama` locally")
    body = http.parse_json(event)
    aliases = config.agent_aliases()
    model = str(body.get("model") or next(iter(aliases), ""))
    if model not in aliases:
        raise http.ApiError(400, "bad_model", "Unknown red-team model alias")
    frames = body.get("frames", 4)
    if isinstance(frames, bool) or not isinstance(frames, int) or frames not in config.AGENT_FRAME_CHOICES:
        raise http.ApiError(400, "bad_frames", "frames must be one of 1, 4, or 8")

    now = _now()
    if not store.take_agent_run_slot(cap=config.agent_runs_daily_cap(), now=now):
        raise http.ApiError(429, "daily_cap", "The daily red-team run limit has been reached")
    run_id = ids.new_id("run")
    store.create_run(
        {
            "runId": run_id,
            "status": "queued",
            "model": model,
            "modelId": aliases[model],
            "frames": frames,
            "progress": 0,
            "rounds": [],
            "passed": False,
            "roundsCorrect": 0,
            "error": None,
            "createdAt": now,
            "ttl": now + config.RECORD_TTL_S,
        }
    )
    try:
        worker_name = os.environ["WORKER_FUNCTION_NAME"]
        response = _lambda_client().invoke(
            FunctionName=worker_name,
            InvocationType="Event",
            Payload=json.dumps({"runId": run_id}).encode("utf-8"),
        )
        if int(response.get("StatusCode", 0)) != 202:
            raise RuntimeError("worker invocation was not accepted")
    except Exception as exc:
        message = f"queue_error: {type(exc).__name__}"
        store.update_run(run_id, status="error", error=message, finishedAt=_now())
        log.log_event("agent_run_error", runId=run_id, error=message)
        raise http.ApiError(503, "agent_unavailable", "The red-team worker could not be queued") from exc
    log.log_event("agent_run_queued", runId=run_id, model=model, frames=frames)
    return http.ok({"runId": run_id, "status": "queued"}, 202)


def _public_agent_run(run: dict[str, Any]) -> dict[str, Any]:
    status = str(run.get("status", "queued"))
    public = {key: value for key, value in run.items() if key not in {"PK", "SK", "ttl", "rounds"}}
    rounds: list[dict[str, Any]] = []
    for item in run.get("rounds") or []:
        round_result = dict(item)
        frame_keys = round_result.pop("frameKeys", [])
        if frame_keys:
            bucket = os.environ["ARTIFACTS_BUCKET"]
            round_result["frameUrls"] = [
                _s3_client().generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": str(frame_key)},
                    ExpiresIn=900,
                )
                for frame_key in frame_keys
            ]
        if status != "done":
            round_result.pop("truth", None)
            round_result.pop("correct", None)
        rounds.append(round_result)
    public["rounds"] = rounds
    return public


def _agent_replay(run: dict[str, Any]) -> dict[str, Any] | None:
    challenge_id = str(run.get("challengeId", ""))
    if not challenge_id:
        return None
    item = store.table().get_item(Key={"PK": f"CH#{challenge_id}", "SK": "META"}).get("Item")
    if not item or not item.get("seedHex"):
        return None
    return mdg.generate_challenge(bytes.fromhex(str(item["seedHex"])))["public"]


def get_agent_run(event: dict[str, Any], params: dict[str, str]) -> dict:
    run_id = params.get("runId", "")
    if not ids.RUN_ID_RE.fullmatch(run_id):
        raise http.ApiError(404, "not_found", "Agent run not found")
    run = store.get_run(run_id)
    if not run:
        raise http.ApiError(404, "not_found", "Agent run not found")
    result = _public_agent_run(run)
    query = event.get("queryStringParameters") or {}
    if run.get("status") == "done" and query.get("replay") == "1":
        replay = _agent_replay(run)
        if replay is not None:
            result["replay"] = replay
    return http.ok(result)


def handoff_not_implemented(_event: dict[str, Any], _params: dict[str, str] | None = None) -> dict:
    raise http.ApiError(501, "not_implemented", "Phone handoff is not implemented yet")


ROUTES = {
    "GET /v1/health": health,
    "POST /v1/challenges": create_challenge,
    "POST /v1/challenges/{challengeId}/answers": answer_challenge,
    "GET /v1/stats": get_stats,
    "POST /v1/agent-runs": start_agent_run,
    "GET /v1/agent-runs/{runId}": get_agent_run,
    "POST /v1/handoffs": handoff_not_implemented,
    "GET /v1/handoffs/{handoffId}": handoff_not_implemented,
}


def handler(event: dict[str, Any], _context: object) -> dict:
    try:
        route, params = http.match_route(event, ROUTES)
        if route is None:
            return http.error(404, "not_found", "Route not found")
        return route(event, params)
    except http.ApiError as exc:
        return http.error(exc.status, exc.code, exc.message)
    except Exception:
        log.get_logger().exception("api_internal_error")
        return http.error(500, "internal", "Internal server error")
