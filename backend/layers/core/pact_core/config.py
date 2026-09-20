"""Runtime configuration shared by the Lambda handlers and local tests."""

from __future__ import annotations

import os

CHALLENGE_TTL_S = 180
TOKEN_TTL_S = 120
RECORD_TTL_S = 7 * 24 * 3600
ACCOUNT_DAILY_QUOTA = 2
AGENT_FRAME_CHOICES = (1, 4, 8)
FAMILIES = ("mdg-v1", "imu-v1")
TRACE_MAX_BYTES = 512_000
HANDOFF_TTL_S = 300

STAGE = os.environ.get("STAGE", "dev")
LOCAL_DEV = os.environ.get("PACT_LOCAL_DEV") == "1"


def table_name() -> str:
    return os.environ["TABLE_NAME"]


def ddb_endpoint() -> str | None:
    return os.environ.get("PACT_DDB_ENDPOINT") or None


def agent_aliases() -> dict[str, str]:
    """Parse the deployment's stable ``alias=model-id`` list."""
    raw = os.environ.get("AGENT_MODELS", "")
    aliases: dict[str, str] = {}
    for part in raw.split(","):
        if "=" not in part:
            continue
        alias, model_id = part.split("=", 1)
        if alias.strip() and model_id.strip():
            aliases[alias.strip()] = model_id.strip()
    return aliases


def agent_runs_daily_cap() -> int:
    return int(os.environ.get("AGENT_RUNS_DAILY_CAP", "300"))
