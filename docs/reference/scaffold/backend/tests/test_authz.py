import time

import authz
import jwt
import pytest
from pact_core import tokens

SECRET = "x" * 64


@pytest.mark.parametrize(
    "assurance,replayed,today,decision,policies",
    [
        ("motion", False, 0, "ALLOW", ["permit-motion-book"]),
        ("motion", True, 0, "DENY", ["forbid-token-replay"]),
        ("account", False, 0, "ALLOW", ["permit-account-book-with-quota"]),
        ("account", False, 1, "ALLOW", ["permit-account-book-with-quota"]),
        ("account", False, 2, "DENY", []),
        ("account", True, 0, "DENY", ["forbid-token-replay"]),
    ],
)
def test_cedar_decisions(assurance, replayed, today, decision, policies):
    out = authz.decide(
        sub='v-1"quote', assurance=assurance, action="BookTicket", token_replayed=replayed, bookings_today=today
    )
    assert out["decision"] == decision and out["policies"] == policies and out["errors"] == []


def test_token_roundtrip_and_claims():
    tok, claims = tokens.mint(SECRET, sub="v-1", assurance="motion", challenge_id="c-1")
    got = tokens.verify(SECRET, tok)
    assert got["jti"] == claims["jti"] and got["asr"] == "motion" and got["cid"] == "c-1"


def test_token_rejects_tamper_expiry_and_wrong_key():
    tok, _ = tokens.mint(SECRET, sub="v-1", assurance="motion")
    with pytest.raises(jwt.PyJWTError):
        tokens.verify("y" * 64, tok)
    old, _ = tokens.mint(SECRET, sub="v-1", assurance="motion", now=int(time.time()) - 600)
    with pytest.raises(jwt.ExpiredSignatureError):
        tokens.verify(SECRET, old)
    head, body, sig = tok.split(".")
    with pytest.raises(jwt.PyJWTError):
        tokens.verify(SECRET, ".".join([head, body[:-2] + "AA", sig]))
