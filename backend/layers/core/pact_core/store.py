"""DynamoDB single-table access layer.

All expression attributes are aliased because names such as ``status`` and
``ttl`` are reserved or have changed status across DynamoDB versions.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

import boto3
from botocore.exceptions import ClientError

from . import config


class ChallengeNotFound(Exception):
    pass


class ChallengeExpired(Exception):
    pass


class ChallengeAlreadyUsed(Exception):
    pass


class HandoffNotFound(Exception):
    pass


class HandoffExpired(Exception):
    pass


@lru_cache(maxsize=4)
def _table(endpoint: str | None, name: str):
    resource = boto3.resource("dynamodb", region_name="us-east-1", endpoint_url=endpoint)
    return resource.Table(name)


def table():
    return _table(config.ddb_endpoint(), config.table_name())


def put_challenge(
    challenge_id: str,
    *,
    seed_hex: str,
    cohort: str,
    family: str,
    now: int,
    expires_at: int,
    answers: list[str] | None = None,
    handoff_id: str | None = None,
) -> None:
    item: dict[str, Any] = {
        "PK": f"CH#{challenge_id}",
        "SK": "META",
        "family": family,
        "seedHex": seed_hex,
        "cohort": cohort,
        "status": "issued",
        "createdAt": now,
        "expiresAt": expires_at,
        "ttl": now + config.RECORD_TTL_S,
    }
    if answers is not None:
        item["answers"] = answers
    if handoff_id is not None:
        item["handoffId"] = handoff_id
    table().put_item(Item=item)


def consume_challenge(challenge_id: str, *, now: int) -> dict:
    try:
        result = table().update_item(
            Key={"PK": f"CH#{challenge_id}", "SK": "META"},
            UpdateExpression="SET #s = :answered, #answered = :now",
            ConditionExpression="attribute_exists(#pk) AND #s = :issued AND #expires >= :now",
            ExpressionAttributeNames={
                "#pk": "PK",
                "#s": "status",
                "#answered": "answeredAt",
                "#expires": "expiresAt",
            },
            ExpressionAttributeValues={":answered": "answered", ":issued": "issued", ":now": now},
            ReturnValues="ALL_NEW",
        )
        return dict(result["Attributes"])
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
            raise
        item = table().get_item(Key={"PK": f"CH#{challenge_id}", "SK": "META"}).get("Item")
        if not item:
            raise ChallengeNotFound(challenge_id) from exc
        if item.get("status") != "issued":
            raise ChallengeAlreadyUsed(challenge_id) from exc
        if int(item.get("expiresAt", 0)) < now:
            raise ChallengeExpired(challenge_id) from exc
        raise ChallengeNotFound(challenge_id) from exc


def record_attempt(
    *,
    cohort: str,
    family: str,
    passed: bool,
    rounds_correct: int,
    rounds_total: int,
    duration_ms: int,
    now: int | None = None,
) -> None:
    now = int(now if now is not None else datetime.now(UTC).timestamp())
    table().update_item(
        Key={"PK": f"STATS#{family}", "SK": f"COHORT#{cohort}"},
        UpdateExpression=(
            "ADD #attempts :one, #passes :passes, #correct :correct, "
            "#total :total, #duration :duration SET #updated = :now"
        ),
        ExpressionAttributeNames={
            "#attempts": "attempts",
            "#passes": "passes",
            "#correct": "roundsCorrect",
            "#total": "roundsTotal",
            "#duration": "durationMsTotal",
            "#updated": "updatedAt",
        },
        ExpressionAttributeValues={
            ":one": 1,
            ":passes": 1 if passed else 0,
            ":correct": int(rounds_correct),
            ":total": int(rounds_total),
            ":duration": int(duration_ms),
            ":now": now,
        },
    )


def get_stats(family: str) -> list[dict]:
    result = table().query(
        KeyConditionExpression="#pk = :pk",
        ExpressionAttributeNames={"#pk": "PK"},
        ExpressionAttributeValues={":pk": f"STATS#{family}"},
    )
    return [dict(item) for item in result.get("Items", [])]


def mark_jti_used(jti: str, *, exp: int, now: int) -> bool:
    try:
        table().put_item(
            Item={
                "PK": f"JTI#{jti}",
                "SK": "USED",
                "usedAt": now,
                "exp": exp,
                "ttl": exp + 3600,
            },
            ConditionExpression="attribute_not_exists(#pk)",
            ExpressionAttributeNames={"#pk": "PK"},
        )
        return True
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return False
        raise


def is_jti_used(jti: str) -> bool:
    return "Item" in table().get_item(Key={"PK": f"JTI#{jti}", "SK": "USED"})


def _today(now: int | None = None) -> str:
    stamp = datetime.fromtimestamp(now, UTC) if now is not None else datetime.now(UTC)
    return stamp.strftime("%Y-%m-%d")


def get_bookings_today(sub: str, *, now: int | None = None) -> int:
    item = table().get_item(Key={"PK": f"QUOTA#{sub}", "SK": _today(now)}).get("Item")
    return int(item.get("n", 0)) if item else 0


def incr_bookings_today(sub: str, *, now: int | None = None) -> int:
    now = int(now if now is not None else datetime.now(UTC).timestamp())
    result = table().update_item(
        Key={"PK": f"QUOTA#{sub}", "SK": _today(now)},
        UpdateExpression="ADD #n :one SET #ttl = :ttl",
        ExpressionAttributeNames={"#n": "n", "#ttl": "ttl"},
        ExpressionAttributeValues={":one": 1, ":ttl": now + 2 * 24 * 3600},
        ReturnValues="UPDATED_NEW",
    )
    return int(result["Attributes"]["n"])


def put_booking(booking: dict, *, now: int | None = None) -> None:
    now = int(now if now is not None else datetime.now(UTC).timestamp())
    item = dict(booking)
    booking_id = str(item["bookingId"])
    item.update({"PK": f"BOOKING#{booking_id}", "SK": "META", "ttl": now + config.RECORD_TTL_S})
    table().put_item(Item=item)


def take_agent_run_slot(*, cap: int, now: int | None = None) -> bool:
    now = int(now if now is not None else datetime.now(UTC).timestamp())
    try:
        table().update_item(
            Key={"PK": "LIMIT#agent-runs", "SK": _today(now)},
            UpdateExpression="ADD #n :one SET #ttl = :ttl",
            ConditionExpression="attribute_not_exists(#n) OR #n < :cap",
            ExpressionAttributeNames={"#n": "n", "#ttl": "ttl"},
            ExpressionAttributeValues={":one": 1, ":cap": int(cap), ":ttl": now + 2 * 24 * 3600},
        )
        return True
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return False
        raise


def create_run(run: dict) -> None:
    item = dict(run)
    run_id = str(item["runId"])
    item.update({"PK": f"RUN#{run_id}", "SK": "META"})
    table().put_item(Item=item)


def update_run(run_id: str, **fields: object) -> None:
    if not fields:
        return
    names = {f"#f{i}": key for i, key in enumerate(fields)}
    values = {f":v{i}": value for i, value in enumerate(fields.values())}
    expression = "SET " + ", ".join(f"{name} = :v{i}" for i, name in enumerate(names))
    table().update_item(
        Key={"PK": f"RUN#{run_id}", "SK": "META"},
        UpdateExpression=expression,
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
    )


def get_run(run_id: str) -> dict | None:
    return table().get_item(Key={"PK": f"RUN#{run_id}", "SK": "META"}).get("Item")


def create_handoff(
    handoff_id: str,
    *,
    poll_key_hash: str,
    phone_key_hash: str,
    now: int,
    expires_at: int,
) -> None:
    table().put_item(
        Item={
            "PK": f"HO#{handoff_id}",
            "SK": "META",
            "pollKeyHash": poll_key_hash,
            "phoneKeyHash": phone_key_hash,
            "status": "pending",
            "createdAt": now,
            "expiresAt": expires_at,
            "ttl": now + 24 * 3600,
        }
    )


def _hash_key(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def check_handoff_phone(handoff_id: str, *, phone_key_hash: str, now: int) -> None:
    item = get_handoff(handoff_id)
    if not item or item.get("phoneKeyHash") != phone_key_hash:
        raise HandoffNotFound(handoff_id)
    if int(item.get("expiresAt", 0)) < now:
        raise HandoffExpired(handoff_id)


def verify_handoff(
    handoff_id: str,
    *,
    phone_key_hash: str,
    token: str,
    challenge_id: str,
    now: int,
) -> bool:
    try:
        table().update_item(
            Key={"PK": f"HO#{handoff_id}", "SK": "META"},
            UpdateExpression="SET #s = :verified, #tok = :token, #cid = :cid, #verified = :now",
            ConditionExpression="#s = :pending AND #phone = :phone AND #expires >= :now",
            ExpressionAttributeNames={
                "#s": "status",
                "#tok": "token",
                "#cid": "challengeId",
                "#verified": "verifiedAt",
                "#phone": "phoneKeyHash",
                "#expires": "expiresAt",
            },
            ExpressionAttributeValues={
                ":verified": "verified",
                ":token": token,
                ":cid": challenge_id,
                ":pending": "pending",
                ":phone": phone_key_hash,
                ":now": now,
            },
        )
        return True
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return False
        raise


def deliver_handoff(handoff_id: str, *, poll_key_hash: str, now: int) -> dict | None:
    try:
        result = table().update_item(
            Key={"PK": f"HO#{handoff_id}", "SK": "META"},
            UpdateExpression="SET #s = :delivered, #delivered = :now REMOVE #tok",
            ConditionExpression="#s = :verified AND #poll = :poll",
            ExpressionAttributeNames={
                "#s": "status",
                "#delivered": "deliveredAt",
                "#tok": "token",
                "#poll": "pollKeyHash",
            },
            ExpressionAttributeValues={
                ":delivered": "delivered",
                ":verified": "verified",
                ":now": now,
                ":poll": poll_key_hash,
            },
            ReturnValues="ALL_OLD",
        )
        return result.get("Attributes")
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return None
        raise


def get_handoff(handoff_id: str) -> dict | None:
    return table().get_item(Key={"PK": f"HO#{handoff_id}", "SK": "META"}).get("Item")


def hash_handoff_key(value: str) -> str:
    return _hash_key(value)
