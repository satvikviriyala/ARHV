"""Lambda authorizer and read-only Cedar explain route."""

from __future__ import annotations

import time
from typing import Any

import authz
import jwt
from pact_core import http, keys, log, store, tokens


def _now() -> int:
    return int(time.time())


def _route_key(event: dict[str, Any]) -> str:
    if event.get("routeKey"):
        return str(event["routeKey"])
    request = event.get("requestContext") or {}
    h = request.get("http") or {}
    return f"{str(h.get('method', '')).upper()} {h.get('path', '')}"


def _deny(reason: str = "default-deny") -> dict:
    return {"isAuthorized": False, "context": {"decision": "DENY", "reason": reason}}


def handler(event: dict[str, Any], _context: object) -> dict:
    jti = None
    try:
        action = authz.ROUTE_ACTIONS.get(_route_key(event))
        if action is None:
            return _deny("unknown_route")
        raw = http.header(event, "x-pact-token")
        if not raw:
            return _deny("missing_token")
        claims = tokens.verify(keys.token_secret(), raw)
        jti = str(claims["jti"])
        now = _now()
        first = store.mark_jti_used(jti, exp=int(claims["exp"]), now=now)
        bookings = store.get_bookings_today(str(claims["sub"]), now=now) if claims.get("asr") == "account" else 0
        decision = authz.decide(
            sub=str(claims["sub"]),
            assurance=str(claims["asr"]),
            action=action,
            token_replayed=not first,
            bookings_today=bookings,
        )
        log.log_event(
            "authz_decision",
            decision=decision["decision"],
            policies=decision["policies"],
            assurance=claims["asr"],
            action=action,
            jti=jti,
            reason="replay" if not first else None,
        )
        return {
            "isAuthorized": decision["decision"] == "ALLOW",
            "context": {
                "sub": str(claims["sub"]),
                "assurance": str(claims["asr"]),
                "jti": jti,
                "decision": decision["decision"],
                "policies": ",".join(decision["policies"]) or "default-deny",
            },
        }
    except jwt.PyJWTError:
        return _deny("invalid_token")
    except Exception:
        log.get_logger().exception("authorizer_internal_error", extra={"jti": jti})
        return _deny("internal")


def _invalid_reason(exc: jwt.PyJWTError) -> str:
    if isinstance(exc, jwt.ExpiredSignatureError):
        return "expired"
    if isinstance(exc, jwt.InvalidSignatureError):
        return "bad_signature"
    return "malformed"


def explain_handler(event: dict[str, Any], _context: object) -> dict:
    try:
        body = http.parse_json(event)
        raw = body.get("token") or http.header(event, "x-pact-token")
        if not isinstance(raw, str) or not raw:
            return http.ok({"tokenValid": False, "reason": "malformed"})
        try:
            claims = tokens.verify(keys.token_secret(), raw)
        except jwt.PyJWTError as exc:
            return http.ok({"tokenValid": False, "reason": _invalid_reason(exc)})
        now = _now()
        sub, assurance = str(claims["sub"]), str(claims["asr"])
        bookings = store.get_bookings_today(sub, now=now) if assurance == "account" else 0
        decision = authz.decide(
            sub=sub,
            assurance=assurance,
            action="BookTicket",
            token_replayed=store.is_jti_used(str(claims["jti"])),
            bookings_today=bookings,
        )
        public_claims = {key: claims[key] for key in ("sub", "asr", "prf", "exp", "jti") if key in claims}
        return http.ok(
            {
                "tokenValid": True,
                "claims": public_claims,
                "replayed": store.is_jti_used(str(claims["jti"])),
                "bookingsToday": bookings,
                "action": "BookTicket",
                "decision": decision["decision"],
                "policies": decision["policies"],
            }
        )
    except http.ApiError as exc:
        return http.error(exc.status, exc.code, exc.message)
    except Exception:
        log.get_logger().exception("explain_internal_error")
        return http.error(500, "internal", "Internal server error")
