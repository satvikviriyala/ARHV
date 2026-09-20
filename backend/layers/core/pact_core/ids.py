"""Opaque identifiers and analytics-label validation."""

from __future__ import annotations

import re
import secrets

CHALLENGE_ID_RE = re.compile(r"^ch_[0-9a-f]{24}$")
RUN_ID_RE = re.compile(r"^run_[0-9a-f]{24}$")
HANDOFF_ID_RE = re.compile(r"^ho_[0-9a-f]{24}$")
KEY_RE = re.compile(r"^[0-9a-f]{32}$")
COHORT_RE = re.compile(r"^(public|study|local|agent:[a-z0-9.-]{1,40}:k[0-9]{1,2})$")


def new_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(12)}"


def new_visitor() -> str:
    return f"v_{secrets.token_hex(8)}"


def sanitize_cohort(value: object) -> str:
    candidate = str(value or "").strip().lower()
    return candidate if COHORT_RE.fullmatch(candidate) else "public"
