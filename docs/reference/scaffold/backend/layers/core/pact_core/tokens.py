"""PACT humanity tokens: short-lived, single-use HS256 JWTs (PyJWT)."""

from __future__ import annotations

import time
import uuid

import jwt  # PyJWT

ISSUER = "pact"
AUDIENCE = "pact-demo"
TTL_SECONDS = 120
LEEWAY_SECONDS = 5
ASSURANCE_LEVELS = ("motion", "account")


def mint(
    secret: str, *, sub: str, assurance: str, challenge_id: str | None = None, now: int | None = None
) -> tuple[str, dict]:
    if assurance not in ASSURANCE_LEVELS:
        raise ValueError(f"bad assurance {assurance!r}")
    iat = int(now if now is not None else time.time())
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": sub,
        "jti": uuid.uuid4().hex,
        "iat": iat,
        "nbf": iat - 1,
        "exp": iat + TTL_SECONDS,
        "asr": assurance,
    }
    if challenge_id:
        claims["cid"] = challenge_id
    return jwt.encode(claims, secret, algorithm="HS256"), claims


def verify(secret: str, token: str) -> dict:
    """Raises jwt.PyJWTError (or subclass) on any problem: bad signature, expired, wrong aud/iss, missing claims."""
    claims = jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        audience=AUDIENCE,
        issuer=ISSUER,
        leeway=LEEWAY_SECONDS,
        options={"require": ["exp", "iat", "jti", "sub", "asr"]},
    )
    if claims.get("asr") not in ASSURANCE_LEVELS:
        raise jwt.InvalidTokenError("unknown assurance level")
    return claims
