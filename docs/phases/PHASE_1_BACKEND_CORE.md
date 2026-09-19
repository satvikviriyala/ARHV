# PHASE 1: Backend core + deploy (budget 4 h · Sat 17:00–21:00 IST)

**Goal:** the complete human-path backend deployed on AWS: challenge → answers → motion token → Cedar-authorized
booking, plus explain, stats and the account-token route (UI comes later). Agent-run routes return 501 until Phase 3.
**Read first:** `docs/ARCHITECTURE.md` (naming registry!), `docs/BACKEND.md`, `docs/API.md`, `docs/DATA_MODEL.md`,
`docs/AUTHZ_CEDAR.md`, `docs/TESTING.md`, `docs/SELF_CORRECTION.md`.

## Tasks (commit after each numbered task once its tests pass)
**1.1 Utilities** in `backend/layers/core/pact_core/`: `config.py`, `ids.py`, `keys.py`, `log.py`, `http.py` exactly as
specified in docs/BACKEND.md §2. Tests `test_http.py`: `match_route` matches `POST /v1/challenges/{challengeId}/answers`
from `requestContext.http.method` + `rawPath` and extracts `challengeId`; unknown path → no match; `ok()`
serialises `Decimal`; `parse_json` handles base64 bodies and bad JSON (400).

**1.2 `store.py`** + `test_store.py` (moto `mock_aws`; table fixture with PK/SK). Cover every function and the three
challenge exceptions, the conditional expressions, and reserved-word aliasing.

**1.3 `stats.py`** + tests. Expected Wilson values (z = 1.96): `wilson(0,20)` → (0, 0, 0.1611);
`wilson(19,20)` → (0.95, 0.7639, 0.9911); `wilson(15,90)` → (0.1667, 0.1037, 0.2569); `wilson(0,0)` → (0,0,0).
`summarize` orders cohorts study, public, local, then `agent:*`.

**1.4 `functions/api/app.py`** (router + health, create_challenge, answer_challenge, get_stats; agent-run routes → 501
`not_implemented` for now) + `test_api.py` (docs/TESTING.md §2). The positive-path test reads the true answers from
the moto table, mirroring what `smoke.py` will do in the cloud.

**1.5 `functions/authorizer/app.py`** (`handler` + `explain_handler`, fail closed) + `test_authorizer.py` +
`test_quota_sync.py`. Build authorizer events like API Gateway's payload v2 for Lambda authorizers:
`{"type":"REQUEST","routeKey":"POST /v1/demo/bookings","headers":{"x-pact-token": …},"requestContext":{"http":{"method":"POST","path":"/v1/demo/bookings"}}}`.

**1.6 `functions/booking/app.py`** + `test_booking.py` (event with `requestContext.authorizer.lambda` context).

**1.7 `functions/account_token/app.py`** + `test_account_token.py` (event with `requestContext.authorizer.jwt.claims`).

**1.8 `functions/agent_worker/app.py` stub:** `handler` marks `RUN#<runId>` as `error` / `not_implemented` (if it
exists) and returns. It will be replaced in Phase 3.

**1.9 `scripts/smoke.py`** per docs/TESTING.md §4 (steps 1–9; step 10 behind `--no-agent`, default on until Phase 3).

**1.10 Local gate:** `make lint && make test-backend` → all green. Commit.

**1.11 Deploy.**
```bash
make build                      # first container build pulls images (several minutes)
make deploy                     # creates stack pact-dev; writes frontend/.env.*.local
.venv/bin/python scripts/stack_output.py ApiUrl
```
Record ApiUrl, UserPoolId, UserPoolClientId, TableName, bucket in MEMORY Snapshot.

**1.12 Cloud gate.** `make smoke SMOKE_ARGS=--no-agent` → every step OK. `make logs` (or Logs Insights query in
docs/AWS_INFRA.md §8) shows `authz_decision` lines with ALLOW and DENY. Paste a 3-line excerpt into MEMORY Log.

**1.13 Close.** MEMORY (Snapshot, Log, Next Steps = Phase 2) · `git tag phase-1-done` · push.

## Exit gate
- [ ] All backend tests green (≥ 20 reference + your new ones) · lint clean · `sam validate --lint` OK
- [ ] Stack `pact-dev` deployed; outputs recorded
- [ ] `make smoke SMOKE_ARGS=--no-agent` green: pass → token → booking 201 (`permit-motion-book`); replay 403 +
      explain shows `forbid-token-replay`; no header 401; garbage 403; wrong answers → passed false; 409 on re-answer

## If things go wrong
docs/SELF_CORRECTION.md playbooks (layer import, cedarpy wheel, 401/403/500, reserved words, Decimal, ROLLBACK).
Time box: if deploy is still failing at 20:30, keep working on Phase 2 UI against `sam local` (docs/LOCAL_DEV.md)
while resolving the deploy.
