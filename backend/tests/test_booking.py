import json

from conftest import load_handler
from pact_core import store


def booking_event(assurance: str = "physical", policies: str = "permit-physical-book") -> dict:
    return {
        "requestContext": {
            "authorizer": {
                "lambda": {
                    "sub": "v-booker",
                    "assurance": assurance,
                    "policies": policies,
                    "jti": "jti-booker",
                }
            }
        },
        "body": "{}",
    }


def test_booking_returns_fictional_counter_and_policy(ddb_table):
    booking = load_handler("booking")
    response = booking.handler(booking_event(), None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 201
    assert body["policy"] == "permit-physical-book"
    assert body["assurance"] == "physical"
    assert body["counter"] == "Rush Hour Counter (demo)"


def test_account_booking_increments_quota(ddb_table):
    booking = load_handler("booking")
    first = json.loads(booking.handler(booking_event("account", "permit-account-book-with-quota"), None)["body"])
    second = json.loads(booking.handler(booking_event("account", "permit-account-book-with-quota"), None)["body"])
    assert first["bookingsToday"] == 1 and second["bookingsToday"] == 2
    assert store.get_bookings_today("v-booker") == 2
