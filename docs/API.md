# API — HTTP contract (API Gateway HTTP API, base = `VITE_API_URL`)

All bodies are JSON. Errors: `{"error": {"code": "<snake_case>", "message": "<human text>"}}`.
CORS: origins from the `AllowedOrigins` parameter; headers `content-type, authorization, x-pact-token, x-pact-cohort,
x-pact-poll-key`.
Throttling: stage default 25 rps, burst 50. Names match `docs/ARCHITECTURE.md › Naming registry`.

| Method & path | Auth | Handler | Purpose |
|---|---|---|---|
| `GET /v1/health` | none | ApiFunction | liveness |
| `POST /v1/challenges` | none | ApiFunction | new challenge: `mdg-v1` (3 rounds, no answers) or `imu-v1` (tilt targets + nonce) |
| `POST /v1/challenges/{challengeId}/answers` | none | ApiFunction | submit answers (`mdg-v1`) or a sensor trace (`imu-v1`); token on pass |
| `GET /v1/stats` | none | ApiFunction | pass rates per cohort with 95% CIs (`?family=`) |
| `POST /v1/handoffs` | none | ApiFunction | laptop starts a phone handoff (stretch; 501 until implemented) |
| `GET /v1/handoffs/{handoffId}` | `x-pact-poll-key` | ApiFunction | laptop polls; receives the physical token once |
| `POST /v1/agent-runs` | none (daily cap) | ApiFunction | queue a red-team run (cloud only) |
| `GET /v1/agent-runs/{runId}` | none | ApiFunction | poll run progress/results |
| `POST /v1/tokens/account` | **Cognito JWT** (`Authorization: Bearer <ID token>`) | AccountTokenFunction | accessible path token |
| `POST /v1/demo/bookings` | **Lambda authorizer** (`x-pact-token`) → Cedar | BookingFunction | the protected action |
| `POST /v1/authz/explain` | none | ExplainFunction | dry-run Cedar decision for a token (doesn't consume it) |

---
### `GET /v1/health` → 200
`{"ok": true, "stage": "dev", "family": "mdg-v1", "families": ["mdg-v1", "imu-v1"], "agentModels": ["nova-2-lite", "nova-pro"], "cloudAgents": true}`
(`agentModels` = aliases from `AGENT_MODELS`, in order; `cloudAgents` is false when `PACT_LOCAL_DEV=1`.)

### `POST /v1/challenges`
Headers (optional): `x-pact-cohort: study|public|local|agent:<alias>:k<K>` (invalid → `public`).
Body: `{}` · `{"cohort": "study"}` · `{"family": "imu-v1"}` · `{"family": "imu-v1", "handoffId": "ho_…", "phoneKey": "<32 hex>"}` (handoff, stretch).
`family` ∈ `mdg-v1` (default) | `imu-v1`; anything else → 400 `bad_family`.
**201 (`mdg-v1`)**
```json
{ "challengeId": "ch_3f9c0a1b2c3d4e5f6a7b8c9d", "expiresAt": 1789999999,
  "family": "mdg-v1", "width": 160, "height": 160, "dot": 2, "fps": 30, "playback": "pingpong",
  "rounds": [ { "frames": "<base64 per docs/CHALLENGE_MDG.md §4>", "frameCount": 36,
                "options": ["star","moon","plus","circle","arrow","heart"] }, { … }, { … } ] }
```
Never contains `answers`, `specs`, `seed` or `mask` (tested).

**201 (`imu-v1`)** — the targets are the user's instructions, public by design (security = freshness + timing + physics):
```json
{ "challengeId": "ch_…", "expiresAt": 1789999999, "family": "imu-v1", "nonce": "4c1d3a4cb9541fbcf211d67ad6eef281",
  "targets": [ {"dGamma": 0.0, "dBeta": 24.1, "radius": 8.0, "holdMs": 450},
               {"dGamma": 14.2, "dBeta": 14.2, "radius": 8.0, "holdMs": 450},
               {"dGamma": -23.4, "dBeta": 0.0, "radius": 8.0, "holdMs": 450} ],
  "baselineMs": 600, "maxDurationMs": 30000, "sampleHz": 60 }
```
`dGamma`/`dBeta` are degrees relative to the user's own baseline (median of the first `baselineMs`).
Handoff variant: 404 `handoff_not_found` (unknown id or wrong `phoneKey`, same answer for both) · 410 `handoff_expired`.

### `POST /v1/challenges/{challengeId}/answers`
Body: `{"answers": ["star", "heart", "plus"], "timingsMs": [2310, 1870, 2045]}` (`timingsMs` optional).
- **200 pass:** `{"passed": true, "roundsCorrect": 3, "token": "<jwt>", "expiresIn": 120, "assurance": "motion"}`
- **200 fail:** `{"passed": false, "roundsCorrect": 1}`
- 400 `bad_request` (malformed id/body) · 404 `not_found` · 409 `already_answered` (single use) · 410 `expired` (> 180 s)

**`imu-v1` body:** `{"trace": {"challengeId": "ch_…", "nonce": "<from the challenge>", "samples": [[t_ms, beta, gamma,
alpha|null, gx, gy, gz, rAlpha, rBeta, rGamma], …]}}` — one sample per `devicemotion` event (~60 Hz), 30–4,000
samples, numbers rounded to 0.1, `t_ms` from the start of capture; `gx,gy,gz` = `accelerationIncludingGravity`
(m/s², raw browser sign), `r*` = `rotationRate` (deg/s). Raw body ≤ 512 KB (else 400 `too_large`). The verifier
rules are in `docs/PHYSICAL.md §3`; the challenge is consumed (single use) before verification.
- **200 pass:** `{"passed": true, "token": "<jwt>", "expiresIn": 120, "assurance": "physical", "proof": "imu-v1",
  "metrics": {"n": 319, "durationMs": 5301, "tiltErrDeg": 1.34, "gyroCorr": [0.993, 0.997], "gravityFrac": 1.0, …}}`
  (handoff challenge: no token here; `{"passed": true, "handoff": "verified"}` and the laptop collects it)
- **200 fail:** `{"passed": false, "reasons": ["gravity", "tilt", "gyro"], "metrics": {…}}` — reasons ⊆
  `binding, size, format, timing, continuity, gravity, tilt, gyro, targets` (public rules; Kerckhoffs). Metric
  values above are from a simulator run, for shape only.

### `GET /v1/stats` → 200
Query `?family=mdg-v1|imu-v1` (default `mdg-v1`). For `imu-v1`, `"chance": null` and `roundAccuracy` = targets reached / 3.
```json
{ "family": "mdg-v1", "generatedAt": 1789999999, "chance": {"round": 0.1667, "pass": 0.0046},
  "cohorts": [ { "cohort": "study", "attempts": 24, "passes": 23, "passRate": 0.958, "passCi": [0.798, 0.993],
                 "roundAccuracy": 0.986, "roundCi": [0.925, 0.998], "meanMs": 6120 },
               { "cohort": "agent:nova-2-lite:k4", "attempts": 30, "passes": 0, "passRate": 0.0, "passCi": [0.0, 0.114],
                 "roundAccuracy": 0.178, "roundCi": [0.111, 0.272], "meanMs": 0 } ] }
```
(Numbers above are illustrative placeholders for the shape only. Never copy them into docs or the video.)

### `POST /v1/agent-runs` (Phase 3)
Body: `{"model": "nova-2-lite", "frames": 4}`. `model` must be an alias in `AGENT_MODELS`; `frames` ∈ {1, 4, 8}.
- **202** `{"runId": "run_…", "status": "queued"}` · 400 `bad_model`/`bad_frames` · 429 `daily_cap` · 501 `cloud_only` (local)

### `GET /v1/agent-runs/{runId}` → 200
```json
{ "runId": "run_…", "status": "queued|running|done|error", "model": "nova-2-lite", "modelId": "us.amazon.nova-2-lite-v1:0",
  "frames": 4, "progress": 2, "createdAt": 0, "finishedAt": 0, "passed": false, "roundsCorrect": 0, "error": null,
  "rounds": [ { "index": 0, "options": ["…"], "answer": "circle", "confidence": 0.35, "rationale": "…",
                "valid": true, "latencyMs": 4210, "frameUrls": ["https://…presigned…"],
                "truth": "star", "correct": false } ] }
```
`truth`/`correct` only appear when `status == "done"`. 404 `not_found`.
`GET /v1/agent-runs/{runId}?replay=1` additionally returns `"replay": {<the challenge's public payload: rounds with
frames + options>}` **only when `status == "done"`** (regenerated deterministically from the stored seed; the
challenge is already consumed, so this reveals nothing usable). Used by the Lab's "What you see" canvas.

### `POST /v1/tokens/account`
Header `Authorization: Bearer <Cognito ID token>` (API Gateway validates issuer and audience first → 401 if invalid).
- **200** `{"token": "<jwt>", "expiresIn": 120, "assurance": "account", "bookingsToday": 0, "dailyQuota": 2}`
- 401 (no/invalid JWT) · 403 `email_unverified`

### `POST /v1/demo/bookings`
Header `x-pact-token: <jwt>`. Body `{}`.
- **201** `{"bookingId": "bk_…", "pnr": "4821930675", "seat": "B2-34", "counter": "Rush Hour Counter (demo)",
  "assurance": "motion", "policy": "permit-motion-book", "createdAt": 0}` (+ `"bookingsToday": n` for account)
- **401** header missing (API Gateway rejects before the authorizer runs)
- **403** authorizer denied (bad/expired token, replay, quota): body `{"message":"Forbidden"}` from API Gateway.
  Use `/v1/authz/explain` to see *why*.

### `POST /v1/handoffs` (stretch, S5) — laptop → phone
Body `{}`. **201** `{"handoffId": "ho_<24 hex>", "pollKey": "<32 hex>", "phoneKey": "<32 hex>", "expiresAt": 1789999999}`
(TTL 300 s). The laptop builds `phoneUrl = ${location.origin}/phone?h=<handoffId>&k=<phoneKey>` and shows it as a QR.
Only SHA-256 hashes of both keys are stored. 501 `not_implemented` until S5 ships.

### `GET /v1/handoffs/{handoffId}` (stretch, S5)
Header `x-pact-poll-key: <pollKey>`. Poll every 1.5 s.
- **200** `{"status": "pending"}` → phone not done yet
- **200** `{"status": "verified", "token": "<jwt>", "expiresIn": 120, "assurance": "physical", "proof": "imu-v1"}` —
  returned **once** (atomic `verified → delivered`, token removed from the item)
- **200** `{"status": "delivered"}` on later polls · 404 `not_found` (unknown id **or** wrong poll key) · 410 `expired`

### `POST /v1/authz/explain`
Body `{"token": "<jwt>"}` (or header `x-pact-token`). Never consumes the token.
- **200 valid:** `{"tokenValid": true, "claims": {"sub": "v_…", "asr": "motion|physical|account", "prf": "imu-v1"?, "exp": 0, "jti": "…"},
  "replayed": false, "bookingsToday": 0, "action": "BookTicket", "decision": "ALLOW", "policies": ["permit-motion-book"]}`
- **200 invalid:** `{"tokenValid": false, "reason": "expired|bad_signature|malformed"}`

---
## curl walkthrough (the smoke test automates this; see docs/TESTING.md)
```bash
API=$(.venv/bin/python scripts/stack_output.py ApiUrl)
curl -s $API/v1/health
CH=$(curl -s -X POST $API/v1/challenges -H 'content-type: application/json' -d '{}')
CID=$(echo "$CH" | python3 -c 'import sys,json;print(json.load(sys.stdin)["challengeId"])')
curl -s -X POST $API/v1/challenges/$CID/answers -H 'content-type: application/json' -d '{"answers":["circle","circle","circle"]}'
curl -s -o /dev/null -w '%{http_code}\n' -X POST $API/v1/demo/bookings              # 401 (no header)
curl -s -o /dev/null -w '%{http_code}\n' -X POST $API/v1/demo/bookings -H 'x-pact-token: nope'   # 403
curl -s -X POST $API/v1/challenges -H 'content-type: application/json' -d '{"family":"imu-v1"}'   # tilt targets + nonce
.venv/bin/python scripts/imu_attack_demo.py --api $API   # spoofs vs the live verifier (physics-consistent sim passes)
```
