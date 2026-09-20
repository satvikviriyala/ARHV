import json

from conftest import load_handler
from pact_core import config, tokens

SECRET = "local-test-secret-" + "x" * 48


def account_event(claims: dict | None) -> dict:
    return {"requestContext": {"authorizer": {"jwt": {"claims": claims or {}}}}}


def test_verified_claims_mint_account_token(ddb_table):
    handler = load_handler("account_token")
    response = handler.handler(account_event({"sub": "cognito-user", "email_verified": "true"}), None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert tokens.verify(SECRET, body["token"])["asr"] == "account"
    assert body["dailyQuota"] == 2


def test_unverified_and_missing_claims_are_rejected(ddb_table):
    handler = load_handler("account_token")
    assert handler.handler(account_event({"sub": "u", "email_verified": "false"}), None)["statusCode"] == 403
    assert handler.handler(account_event(None), None)["statusCode"] == 401
    config.LOCAL_DEV = True
    local = json.loads(handler.handler(account_event(None), None)["body"])
    assert local["assurance"] == "account"
    config.LOCAL_DEV = False
