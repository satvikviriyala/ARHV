import pytest
from pact_core import store

NOW = 1_700_000_000


def test_challenge_consumption_is_single_use_and_maps_missing_expired(ddb_table):
    del ddb_table
    store.put_challenge(
        "ch_" + "a" * 24,
        seed_hex="ab" * 32,
        cohort="study",
        family="mdg-v1",
        now=NOW,
        expires_at=NOW + 180,
        answers=["circle", "star", "heart"],
    )
    item = store.consume_challenge("ch_" + "a" * 24, now=NOW + 1)
    assert item["status"] == "answered"
    with pytest.raises(store.ChallengeAlreadyUsed):
        store.consume_challenge("ch_" + "a" * 24, now=NOW + 2)
    with pytest.raises(store.ChallengeNotFound):
        store.consume_challenge("ch_" + "b" * 24, now=NOW)
    store.put_challenge(
        "ch_" + "c" * 24,
        seed_hex="cd" * 32,
        cohort="public",
        family="imu-v1",
        now=NOW - 200,
        expires_at=NOW - 1,
    )
    with pytest.raises(store.ChallengeExpired):
        store.consume_challenge("ch_" + "c" * 24, now=NOW)


def test_jti_quota_agent_cap_and_stats(ddb_table):
    del ddb_table
    assert store.mark_jti_used("jti-1", exp=NOW + 120, now=NOW)
    assert not store.mark_jti_used("jti-1", exp=NOW + 120, now=NOW + 1)
    assert store.is_jti_used("jti-1")
    assert store.get_bookings_today("v-test", now=NOW) == 0
    assert store.incr_bookings_today("v-test", now=NOW) == 1
    assert store.get_bookings_today("v-test", now=NOW) == 1
    assert store.take_agent_run_slot(cap=1, now=NOW)
    assert not store.take_agent_run_slot(cap=1, now=NOW)
    store.record_attempt(
        cohort="study",
        family="imu-v1",
        passed=True,
        rounds_correct=3,
        rounds_total=3,
        duration_ms=5000,
        now=NOW,
    )
    item = store.get_stats("imu-v1")[0]
    assert item["cohort"] == "study"
    assert item["attempts"] == 1 and item["passes"] == 1 and item["roundsCorrect"] == 3


def test_run_and_handoff_lifecycle(ddb_table):
    del ddb_table
    run = {"runId": "run_" + "a" * 24, "status": "queued", "ttl": NOW + 100}
    store.create_run(run)
    store.update_run(run["runId"], status="error", error="not_implemented")
    assert store.get_run(run["runId"])["error"] == "not_implemented"
    hid = "ho_" + "b" * 24
    store.create_handoff(
        hid,
        poll_key_hash=store.hash_handoff_key("1" * 32),
        phone_key_hash=store.hash_handoff_key("2" * 32),
        now=NOW,
        expires_at=NOW + 300,
    )
    store.check_handoff_phone(hid, phone_key_hash=store.hash_handoff_key("2" * 32), now=NOW)
    assert store.verify_handoff(
        hid,
        phone_key_hash=store.hash_handoff_key("2" * 32),
        token="not-a-real-token",
        challenge_id="ch_" + "c" * 24,
        now=NOW,
    )
    delivered = store.deliver_handoff(hid, poll_key_hash=store.hash_handoff_key("1" * 32), now=NOW + 1)
    assert delivered["token"] == "not-a-real-token"
    assert store.deliver_handoff(hid, poll_key_hash=store.hash_handoff_key("1" * 32), now=NOW + 2) is None
