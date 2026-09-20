"""Fictional protected booking action."""

from __future__ import annotations

import secrets
import time
from typing import Any

from pact_core import http, ids, log, store


def handler(event: dict[str, Any], _context: object) -> dict:
    request = event.get("requestContext") or {}
    authorizer = request.get("authorizer") or {}
    context = authorizer.get("lambda") or authorizer.get("lambdaAuthorizer") or {}
    if not context:
        return http.error(403, "forbidden", "Authorization context missing")
    now = int(time.time())
    assurance = str(context.get("assurance", ""))
    sub = str(context.get("sub", ""))
    policy = str(context.get("policies", "default-deny")).split(",", 1)[0]
    bookings_today = None
    if assurance == "account":
        bookings_today = store.incr_bookings_today(sub, now=now)
    booking_id = ids.new_id("bk")
    booking = {
        "bookingId": booking_id,
        "pnr": f"{secrets.randbelow(10**10):010d}",
        "seat": f"B{secrets.randbelow(4) + 1}-{secrets.randbelow(40) + 1}",
        "counter": "Rush Hour Counter (demo)",
        "assurance": assurance,
        "policy": policy,
        "sub": sub,
        "createdAt": now,
    }
    if bookings_today is not None:
        booking["bookingsToday"] = bookings_today
    store.put_booking(booking, now=now)
    log.log_event("booking_created", bookingId=booking_id, sub=sub, assurance=assurance, policy=policy)
    return http.ok(booking, 201)
