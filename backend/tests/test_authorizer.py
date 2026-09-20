import json
import time

from conftest import load_handler
from pact_core import tokens

SECRET = "local-test-secret-" + "x" * 48


def auth_event(token: str | None) -> dict:
    return {
        "type": "REQUEST",
        "routeKey": "POST /v1/demo/bookings",
        "headers": {"x-pact-token": token} if token is not None else {},
        "requestContext": {"http": {"method": "POST", "path": "/v1/demo/bookings"}},
    }


def test_physical_token_allows_then_replay_denies(ddb_table):
    authorizer = load_handler("authorizer")
    token, claims = tokens.mint(SECRET, sub="v-1", assurance="physical", proof="imu-v1")
    first = authorizer.handler(auth_event(token), None)
    assert first["isAuthorized"]
    assert "permit-physical-book" in first["context"]["policies"]
    second = authorizer.handler(auth_event(token), None)
    assert not second["isAuthorized"]
    assert second["context"]["decision"] == "DENY"
    explained = authorizer.explain_handler({"body": json.dumps({"token": token})}, None)
    body = json.loads(explained["body"])
    assert body["decision"] == "DENY" and body["replayed"]
    assert claims["jti"] in body["claims"]["jti"]


def test_missing_invalid_expired_and_wrong_key_deny(ddb_table):
    authorizer = load_handler("authorizer")
    assert not authorizer.handler(auth_event(None), None)["isAuthorized"]
    assert not authorizer.handler(auth_event("garbage"), None)["isAuthorized"]
    old, _ = tokens.mint(SECRET, sub="v-1", assurance="motion", now=int(time.time()) - 600)
    assert not authorizer.handler(auth_event(old), None)["isAuthorized"]
    wrong, _ = tokens.mint("y" * 64, sub="v-1", assurance="motion")
    assert not authorizer.handler(auth_event(wrong), None)["isAuthorized"]
    invalid = authorizer.explain_handler({"body": json.dumps({"token": old})}, None)
    assert json.loads(invalid["body"])["reason"] == "expired"
    malformed = authorizer.explain_handler({"body": json.dumps({"token": "garbage"})}, None)
    assert json.loads(malformed["body"])["reason"] in {"malformed", "bad_signature"}


def test_account_quota_is_denied_on_third_booking(ddb_table):
    authorizer = load_handler("authorizer")
    for _ in range(2):
        token, _ = tokens.mint(SECRET, sub="account-1", assurance="account")
        result = authorizer.handler(auth_event(token), None)
        assert result["isAuthorized"]
        from pact_core import store

        store.incr_bookings_today("account-1")
    token, _ = tokens.mint(SECRET, sub="account-1", assurance="account")
    result = authorizer.handler(auth_event(token), None)
    assert not result["isAuthorized"]
