"""Cedar decision helper shared by the Lambda authorizer, the /v1/authz/explain route and tests."""

from __future__ import annotations

import functools
import json
import os

import cedarpy

HERE = os.path.dirname(os.path.abspath(__file__))
CEDAR_DIR = os.environ.get("CEDAR_DIR", os.path.join(HERE, "cedar"))
ROUTE_ACTIONS = {"POST /v1/demo/bookings": "BookTicket"}
COUNTER_ID = "rush-hour-counter"


@functools.lru_cache(maxsize=1)
def _load() -> tuple[str, str, dict[str, str]]:
    with open(os.path.join(CEDAR_DIR, "policies.cedar"), encoding="utf-8") as f:
        policies = f.read()
    with open(os.path.join(CEDAR_DIR, "schema.cedarschema"), encoding="utf-8") as f:
        schema = f.read()
    static = json.loads(cedarpy.policies_to_json_str(policies))["staticPolicies"]
    names = {pid: (p.get("annotations") or {}).get("id", pid) for pid, p in static.items()}
    return policies, schema, names


def decide(*, sub: str, assurance: str, action: str, token_replayed: bool, bookings_today: int) -> dict:
    policies, schema, names = _load()
    entities = [
        {"uid": {"__entity": {"type": "Pact::Visitor", "id": sub}}, "attrs": {"assurance": assurance}, "parents": []},
        {
            "uid": {"__entity": {"type": "Pact::Counter", "id": COUNTER_ID}},
            "attrs": {"kind": "high_demand"},
            "parents": [],
        },
    ]
    request = {
        # dict form: no string escaping, so a hostile `sub` can't break the Cedar request
        "principal": {"type": "Pact::Visitor", "id": sub},
        "action": {"type": "Pact::Action", "id": action},
        "resource": {"type": "Pact::Counter", "id": COUNTER_ID},
        "context": {"tokenReplayed": bool(token_replayed), "bookingsToday": int(bookings_today)},
    }
    result = cedarpy.is_authorized(request, policies, entities, schema)
    return {
        "decision": "ALLOW" if result.allowed else "DENY",
        "policies": [names.get(p, p) for p in result.diagnostics.reasons],
        "errors": [str(e) for e in result.diagnostics.errors],
    }
