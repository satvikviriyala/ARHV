"""Cognito-verified account to accessible PACT token exchange."""

from __future__ import annotations

import time
from typing import Any

from pact_core import config, http, keys, log, store, tokens


def handler(event: dict[str, Any], _context: object) -> dict:
    request = event.get("requestContext") or {}
    authorizer = request.get("authorizer") or {}
    jwt_context = authorizer.get("jwt") or {}
    claims = jwt_context.get("claims") or {}
    if not claims:
        if config.LOCAL_DEV:
            claims = {"sub": "local-dev-user", "email_verified": "true"}
        else:
            return http.error(401, "unauthorized", "Cognito identity required")
    verified = claims.get("email_verified")
    if verified not in (True, "true", "True", 1, "1"):
        return http.error(403, "email_unverified", "Verify the account email first")
    sub = str(claims.get("sub", ""))
    if not sub:
        return http.error(401, "unauthorized", "Cognito subject missing")
    now = int(time.time())
    token, token_claims = tokens.mint(keys.token_secret(), sub=sub, assurance="account", now=now)
    bookings = store.get_bookings_today(sub, now=now)
    log.log_event("account_token_minted", sub=sub, jti=token_claims["jti"])
    return http.ok(
        {
            "token": token,
            "expiresIn": config.TOKEN_TTL_S,
            "assurance": "account",
            "bookingsToday": bookings,
            "dailyQuota": config.ACCOUNT_DAILY_QUOTA,
        }
    )
