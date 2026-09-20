import base64
from decimal import Decimal

import pytest
from pact_core import http


def test_route_match_extracts_challenge_id():
    fn = object()
    route, params = http.match_route(
        {"requestContext": {"http": {"method": "POST", "rawPath": "/v1/challenges/ch_" + "a" * 24 + "/answers"}}},
        {"POST /v1/challenges/{challengeId}/answers": fn},
    )
    assert route is fn
    assert params == {"challengeId": "ch_" + "a" * 24}


def test_unknown_route_does_not_match():
    route, params = http.match_route(
        {"requestContext": {"http": {"method": "GET", "rawPath": "/nope"}}},
        {"GET /v1/health": lambda *_: None},
    )
    assert route is None and params == {}


def test_json_helpers_support_decimal_and_base64():
    response = http.ok({"n": Decimal("2")})
    assert '"n":2' in response["body"]
    payload = base64.b64encode(b'{"family":"imu-v1"}').decode()
    assert http.parse_json({"body": payload, "isBase64Encoded": True}) == {"family": "imu-v1"}


def test_bad_json_is_a_client_error():
    with pytest.raises(http.ApiError, match="valid JSON"):
        http.parse_json({"body": "{"})
