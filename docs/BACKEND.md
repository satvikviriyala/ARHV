# BACKEND — pact_core + Lambda handlers

Python 3.12 on arm64. Shared code ships as **PactCoreLayer** (`backend/layers/core/pact_core`, imported as
`from pact_core import …`; Lambda puts it at `/opt/python`). Handlers are thin: parse → call `pact_core` → respond.
HTTP contract: `docs/API.md`. Data model: `docs/DATA_MODEL.md`. Authz: `docs/AUTHZ_CEDAR.md`.

## 1. Global rules
- boto3 clients/resources are created lazily and cached at module scope (one per container).
- DynamoDB endpoint: `endpoint_url=os.environ.get("PACT_DDB_ENDPOINT") or None` (local only; empty in the cloud).
- Every DynamoDB expression uses `ExpressionAttributeNames` for attribute names (STATUS, TTL, … are reserved).
- Never log tokens, seeds, answers of *human* challenges, or secrets. Log ids (`challengeId`, `jti`, `runId`).
- Lambdas never set CORS headers; API Gateway adds them from `CorsConfiguration`.
- Errors go out as `{"error": {"code": "...", "message": "..."}}` with the right status. Unexpected exceptions →
  500 `internal` and `log.exception(...)` (no stack traces in responses).
- Time: `now = int(time.time())` passed down explicitly (easy to test). IDs from `pact_core.ids`.

## 2. `pact_core` modules
### `config.py`
```python
STAGE = os.environ.get("STAGE", "dev")
LOCAL_DEV = os.environ.get("PACT_LOCAL_DEV") == "1"
CHALLENGE_TTL_S = 180            # time to answer
TOKEN_TTL_S = 120                # mirrors tokens.TTL_SECONDS
RECORD_TTL_S = 7 * 24 * 3600     # retention for challenges/runs/bookings
ACCOUNT_DAILY_QUOTA = 2          # must match the Cedar policy literal
AGENT_FRAME_CHOICES = (1, 4, 8)
FAMILIES = ("mdg-v1", "imu-v1")   # proof families accepted by POST /v1/challenges
TRACE_MAX_BYTES = 512_000        # raw request body limit for imu-v1 answers
HANDOFF_TTL_S = 300              # laptop → phone handoff lifetime (stretch)
def table_name() -> str: return os.environ["TABLE_NAME"]
def ddb_endpoint() -> str | None: return os.environ.get("PACT_DDB_ENDPOINT") or None
def agent_aliases() -> dict[str, str]  # parse AGENT_MODELS "a=id,b=id" (same parser as pact_agent.models)
def agent_runs_daily_cap() -> int     # int(AGENT_RUNS_DAILY_CAP or 300)
```
### `ids.py`
`new_id(prefix) -> f"{prefix}_{secrets.token_hex(12)}"`; `new_visitor() -> f"v_{secrets.token_hex(8)}"` (anonymous `sub` for motion tokens).
Regexes: `CHALLENGE_ID_RE = r"^ch_[0-9a-f]{24}$"`, `RUN_ID_RE = r"^run_[0-9a-f]{24}$"`, `HANDOFF_ID_RE = r"^ho_[0-9a-f]{24}$"`,
`KEY_RE = r"^[0-9a-f]{32}$"` (handoff keys = `secrets.token_hex(16)`; store `hashlib.sha256(key).hexdigest()` only).
`COHORT_RE = r"^(public|study|local|agent:[a-z0-9.-]{1,40}:k[0-9]{1,2})$"`. `sanitize_cohort(v) -> str`
lower-cases, maps invalid values to `public`.
### `keys.py`
`token_secret() -> str`: if `PACT_TOKEN_SECRET` is set, return it (local only). Otherwise
`secretsmanager.get_secret_value(SecretId=os.environ["TOKEN_SECRET_ARN"])["SecretString"]`, cached for the container.
### `mdg.py`, `imu.py`, `png.py`, `tokens.py`
Already in the repo and tested; don't rewrite. Public API: `mdg.generate_challenge(seed, rounds=3, frames=36)`,
`mdg.decode_frames(b64)`, `mdg.check_answers(expected, submitted) -> (passed, correct)`, `mdg.FAMILY`;
`imu.generate_challenge(seed) -> dict` (all public: family, nonce, targets, baselineMs, maxDurationMs, sampleHz),
`imu.verify(challenge, challenge_id, trace) -> ImuResult(passed: bool, reasons: list[str], metrics: dict)`,
`imu.FAMILY = "imu-v1"`, `imu.N_TARGETS = 3` (rules: `docs/PHYSICAL.md §3`);
`png.render_frame_png(points, scale=3) -> bytes`; `tokens.mint(secret, sub=, assurance=, challenge_id=, proof=, now=)`
(`assurance` ∈ `motion|physical|account`; `proof` → claim `prf`), `tokens.verify(secret, token) -> claims`
(raises `jwt.PyJWTError`).
### `store.py` (single table; see docs/DATA_MODEL.md for exact items)
```python
class ChallengeNotFound(Exception): ...
class ChallengeExpired(Exception): ...
class ChallengeAlreadyUsed(Exception): ...

def put_challenge(challenge_id, *, seed_hex, cohort, family, now, expires_at, answers=None, handoff_id=None) -> None
    # imu-v1 stores no answers: the server re-derives the challenge from seedHex at verification time
def consume_challenge(challenge_id, *, now) -> dict
    # UpdateItem SET #s=:answered, answeredAt=:now
    # Condition: attribute_exists(PK) AND #s = :issued AND expiresAt >= :now ; ReturnValues=ALL_NEW
    # On ConditionalCheckFailed: GetItem → raise NotFound / Expired / AlreadyUsed accordingly
def record_attempt(*, cohort, family, passed, rounds_correct, rounds_total, duration_ms, now) -> None
    # UpdateItem PK=STATS#<family> SK=COHORT#<cohort>: ADD attempts 1, passes p, roundsCorrect k,
    #   roundsTotal n, durationMsTotal d; SET updatedAt
def get_stats(family) -> list[dict]      # Query PK=STATS#<family>
def mark_jti_used(jti, *, exp, now) -> bool   # PutItem JTI#<jti>/USED, Condition attribute_not_exists(PK); True = first use
def is_jti_used(jti) -> bool
def get_bookings_today(sub, *, now) -> int    # GetItem QUOTA#<sub> / <yyyy-mm-dd UTC>
def incr_bookings_today(sub, *, now) -> int   # UpdateItem ADD #n 1, ReturnValues UPDATED_NEW
def put_booking(booking: dict, *, now) -> None
def take_agent_run_slot(*, cap, now) -> bool  # UpdateItem LIMIT#agent-runs/<date> ADD #n 1, Condition attribute_not_exists(#n) OR #n < :cap
def create_run(run: dict) -> None
def update_run(run_id, **fields) -> None      # SET for each field (names via ExpressionAttributeNames)
def get_run(run_id) -> dict | None
# Handoff (stretch, S5). Item HO#<id>/META; see docs/DATA_MODEL.md
def create_handoff(handoff_id, *, poll_key_hash, phone_key_hash, now, expires_at) -> None
def check_handoff_phone(handoff_id, *, phone_key_hash, now) -> None   # raises HandoffNotFound / HandoffExpired
def verify_handoff(handoff_id, *, phone_key_hash, token, challenge_id, now) -> bool
    # UpdateItem SET #s=:verified, #tok=:t, challengeId=:c, verifiedAt=:now
    # Condition: #s = :pending AND phoneKeyHash = :pk AND expiresAt >= :now
def deliver_handoff(handoff_id, *, poll_key_hash, now) -> dict | None
    # UpdateItem SET #s=:delivered, deliveredAt=:now REMOVE #tok, Condition #s = :verified AND pollKeyHash = :h,
    # ReturnValues=ALL_OLD → the old item carries the token (returned exactly once)
def get_handoff(handoff_id) -> dict | None
```
Numbers come back from DynamoDB as `Decimal`: convert to `int`/`float` before JSON (`http.ok` handles it).
### `stats.py`
```python
CHANCE_ROUND = 1 / 6
CHANCE_PASS = (1 / 6) ** 3
def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]   # (p, lo, hi); (0,0,0) if n==0
def summarize(items: list[dict]) -> list[dict]
    # per cohort: attempts, passes, passRate, passCi[lo,hi], roundAccuracy, roundCi[lo,hi], meanMs
    # order: study, public, local, then agent:* sorted
```
### `http.py`
```python
class ApiError(Exception): (status:int, code:str, message:str)
def ok(body, status=200) -> dict        # {"statusCode", "headers": {"content-type": "application/json"}, "body": json.dumps(body, default=decimal_default)}
def error(status, code, message) -> dict
def parse_json(event) -> dict           # handles isBase64Encoded; {} for empty; ApiError(400,"bad_json") otherwise
def header(event, name) -> str | None   # case-insensitive
def match_route(event, routes: dict[str, Callable]) -> tuple[Callable, dict]
    # Match "METHOD /path/{param}" patterns against requestContext.http.method + rawPath (works in AWS and in
    # `sam local`, which may not set routeKey the same way). Returns (handler_fn, path_params).
```
### `log.py`
`get_logger()` returns a `logging.Logger` at INFO. Lambda's JSON log format renders `extra={...}` as top-level
fields. Helper: `log_event(name, **fields)` → `logger.info(name, extra={"event": name, **fields})`.

## 3. Handlers
### `functions/api/app.py` — `handler(event, context)`
Routes (see docs/API.md): `GET /v1/health`, `POST /v1/challenges`, `POST /v1/challenges/{challengeId}/answers`,
`GET /v1/stats`, `POST /v1/agent-runs`, `GET /v1/agent-runs/{runId}`, `POST /v1/handoffs`, `GET /v1/handoffs/{handoffId}`. Dispatch with `http.match_route`; wrap in
`try: … except ApiError as e: return http.error(...) except Exception: log.exception; return http.error(500, "internal", …)`.
- **create_challenge:** `cohort = sanitize_cohort(header x-pact-cohort or body.cohort)` for every family, then branch
  on `family = body.get("family") or "mdg-v1"` (not in `config.FAMILIES` → 400 `bad_family`). **`imu-v1`:** `cid = ids.new_id("ch")`; `seed = secrets.token_bytes(32)`; `ch = imu.generate_challenge(seed)`; if
  `handoffId`/`phoneKey` present (S5) → `store.check_handoff_phone(...)` (404 `handoff_not_found` / 410
  `handoff_expired`); `store.put_challenge(cid, seed_hex=seed.hex(), cohort, family="imu-v1", now, expires_at,
  handoff_id=…)` with `expires_at = now + CHALLENGE_TTL_S`; log `challenge_created` (cid, cohort, family); return
  **201** `{"challengeId": cid, "expiresAt", **ch}`.
  **`mdg-v1`** (default): `seed = secrets.token_bytes(32)`;
  `ch = mdg.generate_challenge(seed)`; `cid = ids.new_id("ch")`; `store.put_challenge(cid, seed_hex=seed.hex(),
  answers=ch["answers"], cohort, family, now, expires_at=now+CHALLENGE_TTL_S)`; log `challenge_created`
  (cid, cohort); return **201** `{"challengeId": cid, "expiresAt": …, **ch["public"]}`.
- **answer_challenge** dispatch: body has `trace` → imu path; body has `answers` → mdg path; after consuming, if
  `rec["family"]` doesn't match the body type → 400 `wrong_family` (the challenge stays consumed).
- **answer_challenge (`imu-v1`)**: reject raw bodies > `TRACE_MAX_BYTES` (400 `too_large`) before parsing; body
  must contain a `trace` dict (400 `bad_request`). `rec = store.consume_challenge(cid, now)` first (single use,
  same 404/410/409 mapping), then `challenge = imu.generate_challenge(bytes.fromhex(rec["seedHex"]))`,
  `res = imu.verify(challenge, cid, trace)` (never trust any client-side "done"); `store.record_attempt(cohort,
  family="imu-v1", passed, rounds_correct=metrics["targetsReached"], rounds_total=3, duration_ms=metrics["durationMs"])`
  (use `.get(..., 0)`: early failures have few metrics); log `imu_verified` (cid, passed, reasons, metrics; **never
  the samples**). Pass → `tokens.mint(secret, sub=ids.new_visitor(), assurance="physical", challenge_id=cid,
  proof="imu-v1")`; log `token_minted` (jti, cid, asr). If `rec.get("handoffId")` (S5): `store.verify_handoff(...)`
  with the token and return `{"passed": true, "handoff": "verified", "metrics"}` (no token to the phone); else
  return `{"passed": true, "token", "expiresIn": 120, "assurance": "physical", "proof": "imu-v1", "metrics"}`.
  Fail → `{"passed": false, "reasons", "metrics"}`. The consumed challenge can't be retried: the client asks for a
  new one ("Try again").
- **answer_challenge (`mdg-v1`):** validate `challengeId` (regex) and body `answers` (list of 3 strings ≤ 16 chars);
  `timingsMs` optional (list of ints, clamp 0..600000). `rec = store.consume_challenge(cid, now)` → map exceptions
  to 404 `not_found` / 410 `expired` / 409 `already_answered`. `passed, correct = mdg.check_answers(rec["answers"],
  answers)`; `store.record_attempt(cohort=rec["cohort"], …, duration_ms=sum(timingsMs))`. If passed:
  `token, claims = tokens.mint(keys.token_secret(), sub=ids.new_visitor(), assurance="motion", challenge_id=cid)`;
  log `token_minted` (jti, cid). Return **200** `{"passed": true, "roundsCorrect": 3, "token": token,
  "expiresIn": 120, "assurance": "motion"}` or `{"passed": false, "roundsCorrect": correct}`.
- **get_stats:** `family = query family or "mdg-v1"` (must be in `FAMILIES`); `{"family", "chance": {"round": 1/6,
  "pass": 1/216} if mdg-v1 else None, "cohorts": stats.summarize(store.get_stats(family)), "generatedAt": now}`.
- **start_agent_run** (Phase 3): if `LOCAL_DEV` → 501 `cloud_only` ("use `make bench BACKEND=ollama` locally").
  Body `{"model": alias, "frames": 1|4|8}` (defaults: first alias, 4). Unknown alias → 400. If
  `not store.take_agent_run_slot(cap=…)` → 429 `daily_cap`. `run_id = new_id("run")`; `store.create_run({...,
  "status": "queued", "model": alias, "modelId": id, "frames": k, "createdAt": now, "ttl": now+RECORD_TTL_S})`;
  `lambda.invoke(FunctionName=WORKER_FUNCTION_NAME, InvocationType="Event", Payload=json.dumps({"runId": run_id}))`;
  log `agent_run_queued`; return **202** `{"runId", "status": "queued"}`.
- **get_agent_run:** 404 if missing. For each round with `frameKeys`, add `frameUrls` = S3 presigned GET (900 s).
  Only include `truth` and `correct` when `status == "done"`. If query `replay=1` **and** `status == "done"`: load
  `CH#<run.challengeId>`, `replay = mdg.generate_challenge(bytes.fromhex(seedHex))["public"]` and include it.
  Return the run (Decimals converted).
- **health:** `{"ok": true, "stage": STAGE, "family": "mdg-v1", "families": list(FAMILIES), "agentModels": list(config.agent_aliases()), "cloudAgents": not LOCAL_DEV}`.
- **create_handoff** (S5; until then 501 `not_implemented`): `hid = new_id("ho")`, `poll = token_hex(16)`,
  `phone = token_hex(16)`; store hashes; log `handoff_created` (hid); **201** `{"handoffId", "pollKey", "phoneKey", "expiresAt"}`.
- **get_handoff** (S5): validate id + header `x-pact-poll-key` (regexes); item missing or hash mismatch → 404
  `not_found` (same for both); expired → 410; `pending` → `{"status": "pending"}`; `verified` →
  `store.deliver_handoff(...)` → `{"status": "verified", "token", "expiresIn": 120, "assurance": "physical",
  "proof": "imu-v1"}` + log `handoff_delivered`; `delivered` → `{"status": "delivered"}`.

### `functions/authorizer/app.py`
- `handler(event, context)` (HTTP API Lambda authorizer, payload v2, simple responses): read `x-pact-token`
  (headers are lower-case); action = `authz.ROUTE_ACTIONS.get(routeKey)` or from `requestContext.http` method +
  path; unknown → deny. `claims = tokens.verify(...)` (any `jwt.PyJWTError` → deny, reason `invalid_token`).
  `first = store.mark_jti_used(jti, exp=…)`; `bookings = store.get_bookings_today(sub)` if `asr == "account"` else 0;
  `d = authz.decide(sub=…, assurance=asr, action=…, token_replayed=not first, bookings_today=bookings)`.
  Log `authz_decision` with decision, policies, assurance, action, jti, reason. Return `{"isAuthorized": d == ALLOW,
  "context": {"sub", "assurance", "jti", "decision", "policies": ",".join(...) or "default-deny"}}`.
  **Any unexpected exception → log and deny (fail closed).**
- `explain_handler(event, context)` (route `POST /v1/authz/explain`): token from body `token` or header. Invalid →
  200 `{"tokenValid": false, "reason": "expired"|"bad_signature"|"malformed"}`. Valid → `replayed =
  store.is_jti_used(jti)` (read-only), bookings as above, `authz.decide(...)` → 200 `{"tokenValid": true, "claims":
  {sub, asr, exp, jti}, "replayed", "bookingsToday", "decision", "policies", "action": "BookTicket"}`.
- `authz.py` + `cedar/`: copy from the scaffold unchanged.

### `functions/booking/app.py`
Reads `event["requestContext"]["authorizer"]["lambda"]` (sub, assurance, policies, jti). If `assurance ==
"account"`: `used = store.incr_bookings_today(sub)`. Build a **fictional** booking: `bookingId = new_id("bk")`,
`pnr` = 10 digits from `secrets.randbelow`, `seat` like `B2-34`, `counter = "Rush Hour Counter (demo)"`,
`assurance`, `policy`, `bookingsToday` (account only), `createdAt`. `store.put_booking`; log `booking_created`;
return **201**.

### `functions/account_token/app.py`
`claims = requestContext.authorizer.jwt.claims`. If missing: `LOCAL_DEV` → `{"sub": "local-dev-user",
"email_verified": "true"}` else 401. Require `email_verified == "true"` (403 `email_unverified` otherwise).
`token = tokens.mint(..., sub=claims["sub"], assurance="account")`; `bookings = store.get_bookings_today(sub)`.
Log `account_token_minted`. Return 200 `{"token", "expiresIn": 120, "assurance": "account", "bookingsToday",
"dailyQuota": 2}`.

### `functions/agent_worker/app.py` — `handler({"runId": …}, context)`
Implements the full flow in `docs/REDTEAM_AGENT.md §4`: it claims only queued runs, creates the same server-side
`mdg-v1` challenge, uploads K consecutive 3× PNG frames per round to S3, calls a fresh Strands agent for each
round, records progress, scores with `mdg.check_answers`, and records the `agent:<alias>:k<K>` stats cohort. Model
and infrastructure failures set `status=error` and do not record stats; stored run data contains metrics and answers
needed by the Lab, never seeds or raw frame bytes.

## 4. Dependencies (pinned where it matters)
| Where | requirements.txt |
|---|---|
| `layers/core` | `PyJWT>=2.8,<3` |
| `functions/authorizer` | `cedarpy==4.12.0` (verified: wheels for cp312 manylinux x86_64/aarch64 + macOS arm64) |
| `functions/agent_worker` | `strands-agents>=1.56,<2` (verified 1.56.0: `BedrockModel(streaming=False)`, image content blocks) |
| others | none (boto3 comes with the Lambda runtime) |
| dev | `backend/requirements-dev.txt` (pytest, moto, ruff, cedarpy, strands-agents[ollama], numpy, pillow) |
