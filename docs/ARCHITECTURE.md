# ARCHITECTURE — ARHV (codename PACT)

## 1. Overview
A static React app on **Amplify Hosting** talks to one **API Gateway HTTP API**. Anonymous routes (create
challenge, submit answers or a sensor trace, stats, handoffs, agent runs) hit **ApiFunction**, which issues and
verifies both proof families: **`imu-v1`** (phone tilt, physical: the trace is checked with cross-sensor physics in
`pact_core.imu`) and **`mdg-v1`** (motion-defined glyph, perceptual). A pass mints a 120 s single-use token with
`asr=physical` or `asr=motion`. The protected route (`POST /v1/demo/bookings`) is guarded by a **Lambda
authorizer** that verifies the token and asks **Cedar** (via `cedarpy`) for a decision. The accessible route
(`POST /v1/tokens/account`) is guarded by API Gateway's native **JWT authorizer** against **Cognito**. The red team
(**Strands Agents → Amazon Bedrock**) attacks `mdg-v1` through the same public API (`make bench`; the async
**AgentWorkerFunction** + S3 frames power the optional Lab page). All state lives in one **DynamoDB** table; the
token-signing key is generated and held by **Secrets Manager**. Raw sensor traces are never stored.

```mermaid
flowchart LR
  subgraph Phone["Phone browser (HTTPS)"]
    TILT[Tilt check<br/>DeviceMotion + DeviceOrientation<br/>~60 Hz trace]
  end
  subgraph Laptop["Laptop browser"]
    UI[Home · motion puzzle · booking · DevPanel]
  end
  AMP[Amplify Hosting<br/>React + Vite] -. serves .-> Phone & Laptop
  UI -. QR to /phone .-> TILT
  TILT -->|POST /v1/challenges family=imu-v1<br/>POST …/answers trace| APIGW[API Gateway HTTP API]
  UI -->|POST /v1/challenges mdg-v1<br/>POST …/answers| APIGW
  TILT & UI -->|POST /v1/demo/bookings<br/>x-pact-token| APIGW
  UI -->|POST /v1/tokens/account<br/>Bearer Cognito ID token| APIGW
  UI <-->|sign up / sign in| COG[Cognito User Pool]
  APIGW --> API[ApiFunction<br/>imu-v1 physics verifier · mdg-v1 · stats · handoffs]
  APIGW -. Lambda authorizer .-> AUTHZ[AuthorizerFunction<br/>JWT verify + Cedar]
  APIGW --> BOOK[BookingFunction<br/>protected action]
  APIGW -. JWT authorizer .-> COG
  APIGW --> ACCT[AccountTokenFunction]
  APIGW --> EXPL[ExplainFunction<br/>dry-run Cedar]
  BENCH[make bench<br/>Strands Agents] -->|same public API| APIGW
  BENCH --> BR[Amazon Bedrock<br/>Nova 2 Lite · Nova Pro]
  API -. optional Lab .-> WORK[AgentWorkerFunction] --> BR
  WORK --> S3[(S3 frames the AI saw)]
  API & AUTHZ & BOOK & ACCT & EXPL & WORK --> DDB[(DynamoDB pact-dev)]
  API & AUTHZ & ACCT & EXPL --> SM[Secrets Manager<br/>token signing key]
  AUTHZ --> CW[CloudWatch Logs<br/>authz_decision · imu_verified]
```

### 1.1 Proof tiers (what each tier proves, and who decides)
```mermaid
flowchart TB
  subgraph T0["T0 perceptual · mdg-v1 (built)"]
    A0[shape visible only in motion] --> R0[beats screenshot agents today<br/>loses to optical-flow solvers / future video agents]
  end
  subgraph T1["T1 physical, unattested · imu-v1 (built)"]
    A1[fresh random tilt path<br/>server-side cross-sensor physics] --> R1[beats screen-only agents + cheap sensor spoofs<br/>loses to a physics-aware simulator = attestation gap]
  end
  subgraph T2["T2 physical, vendor-attested (proposal)"]
    A2[OS trusted overlay + secure sensor hub<br/>TPM / Secure Enclave / StrongBox signs nonce + gesture] --> R2[beats remote automation and simulators<br/>farms handled by quotas and cost]
  end
  T0 --> TOK[120 s single-use token<br/>asr = motion · physical · physical-attested · account]
  T1 --> TOK
  T2 --> TOK
  TOK --> CEDAR{Cedar policy per action<br/>permit-physical-book · permit-motion-book<br/>forbid-token-replay · quotas}
```

## 2. Trust boundaries (why the functions are split this way)
| Boundary | Function | Can | Cannot |
|---|---|---|---|
| Public, anonymous | ApiFunction | create/consume challenges, verify `imu-v1` traces, mint **physical** and **motion** tokens, run handoffs, read stats, queue agent runs, presign frame URLs | reach Bedrock; perform the protected action; store raw sensor traces |
| Decision point | AuthorizerFunction | verify tokens, mark `jti` used, read quota, evaluate Cedar | perform any action |
| Protected action | BookingFunction | book (fictional), increment account quota | be invoked without an ALLOW from the authorizer |
| Account path | AccountTokenFunction | mint **account** tokens for Cognito-verified users | be invoked without a valid Cognito JWT |
| Read-only explain | ExplainFunction | show the Cedar decision for a token without consuming it | write anything |
| Red team | AgentWorkerFunction | call Bedrock, write frames to S3, record agent stats | mint tokens; be invoked by the API Gateway |

## 3. Flows
### 3.1 Human verification → protected action (motion path)
```mermaid
sequenceDiagram
  participant B as Browser
  participant A as ApiFunction
  participant D as DynamoDB
  participant Z as Authorizer (Cedar)
  participant K as BookingFunction
  B->>A: POST /v1/challenges (x-pact-cohort?)
  A->>A: seed=token_bytes(32), generate_challenge(seed)
  A->>D: put challenge item {answers, seedHex, cohort, expiresAt, status=issued}
  A-->>B: 201 {challengeId, rounds[3]{frames(b64), options[6]}, ...} (no answers)
  Note over B: canvas plays frames ping-pong at 30 fps, user picks 3 shapes
  B->>A: POST /v1/challenges/{id}/answers {answers[3], timingsMs[3]}
  A->>D: conditional update status issued→answered (single use, not expired)
  A->>D: ADD stats counters for cohort
  A-->>B: 200 {passed:true, token, expiresIn:120, assurance:"motion"}
  B->>Z: POST /v1/demo/bookings (x-pact-token)  [API GW invokes authorizer first]
  Z->>Z: verify HS256 JWT (sig, exp, iss, aud)
  Z->>D: put used-jti item if not exists → replayed?
  Z->>Z: cedarpy.is_authorized(...) → ALLOW via permit-motion-book
  Z-->>K: isAuthorized=true + context{sub, assurance, policies}
  K->>D: put booking item
  K-->>B: 201 {bookingId, seat, assurance, policy}
```
### 3.1b Physical path (`imu-v1`, phone tilt)
```mermaid
sequenceDiagram
  participant P as Phone browser
  participant A as ApiFunction
  participant D as DynamoDB
  participant Z as Authorizer (Cedar)
  participant K as BookingFunction
  P->>A: POST /v1/challenges {family:"imu-v1"}
  A->>A: seed=token_bytes(32), imu.generate_challenge(seed) → nonce + 3 random targets
  A->>D: put challenge item {family: imu-v1, seedHex, cohort, expiresAt, status=issued}
  A-->>P: 201 {challengeId, nonce, targets[3], baselineMs, maxDurationMs}
  Note over P: tap → requestPermission (iOS) → ~60 Hz samples (t, β, γ, α, gx, gy, gz, rα, rβ, rγ)<br/>user rolls the dot into each ring and holds
  P->>A: POST /v1/challenges/{id}/answers {trace}
  A->>D: conditional update issued → answered (single use, not expired)
  A->>A: re-derive challenge from seedHex, imu.verify: binding · timing · continuity · gravity · tilt-vs-gravity · gyro · targets
  A->>D: ADD imu-v1 stats counters (metrics only, raw trace discarded)
  A-->>P: 200 {passed:true, token(asr=physical, prf=imu-v1), metrics} or {passed:false, reasons, metrics}
  P->>Z: POST /v1/demo/bookings (x-pact-token)
  Z->>D: put used-jti item if not exists → replayed?
  Z->>Z: Cedar → ALLOW via permit-physical-book
  Z-->>K: isAuthorized=true
  K-->>P: 201 {bookingId, seat, assurance:"physical", policy:"permit-physical-book"}
```
### 3.1c Laptop → phone handoff (stretch)
```mermaid
sequenceDiagram
  participant L as Laptop
  participant A as ApiFunction
  participant P as Phone
  L->>A: POST /v1/handoffs
  A-->>L: {handoffId, pollKey, phoneKey} (only hashes stored, TTL 300 s)
  Note over L: QR encodes /phone?h=handoffId and k=phoneKey
  P->>A: POST /v1/challenges {family:"imu-v1", handoffId, phoneKey}
  P->>A: POST …/answers {trace} → pass → token stored on the handoff item (status verified)
  A-->>P: {passed:true, handoff:"verified"} ("Return to your computer")
  loop every 1.5 s
    L->>A: GET /v1/handoffs/{id} (x-pact-poll-key)
  end
  A-->>L: {status:"verified", token} once (verified → delivered, token removed)
```
### 3.1d The endgame: vendor-attested physical gesture (proposal, docs/PHYSICAL.md §7)
```mermaid
sequenceDiagram
  participant S as Site (ARHV server)
  participant B as Browser
  participant OS as OS trusted overlay
  participant H as Secure sensor hub + TPM/Secure Enclave
  participant I as Token issuer (Privacy Pass)
  S->>B: nonce + signed gesture spec (e.g. tilt path)
  B->>OS: navigator.physical.request({gesture, challenge})
  OS->>H: run gesture UI the page can't draw or drive, evaluate real sensor readings
  H-->>OS: sign {origin, nonce, gestureSpecHash, result, time}
  OS->>I: redeem attestation
  I-->>B: unlinkable token ("a real device saw this fresh gesture")
  B->>S: token → asr = physical-attested → Cedar
```
### 3.2 Accessible path (non-cognitive, WCAG 2.2 SC 3.3.8)
Browser signs up/in with **Cognito** (email code) → `POST /v1/tokens/account` with `Authorization: Bearer <ID token>`
→ API GW JWT authorizer validates issuer/audience → AccountTokenFunction checks `email_verified` → mints a token with
`asr=account` → booking → Cedar `permit-account-book-with-quota` allows while `bookingsToday < 2`.
### 3.3 Red-team run
Browser `POST /v1/agent-runs {model, frames}` → ApiFunction checks alias + daily cap → writes `RUN#id` (queued) →
`lambda.invoke(InvocationType="Event")` → returns 202 `{runId}`. Worker: creates a challenge exactly like a human
gets (cohort `agent:<alias>:k<K>`), renders K consecutive frames per round to PNG (3× scale), uploads them to S3,
asks the Strands agent per round, consumes the challenge, checks answers with the same verifier, records stats,
updates `RUN#id` after each round. Browser polls `GET /v1/agent-runs/{runId}` every 1.5 s and shows the frames via
presigned URLs.

## 4. Naming registry (use these exact names everywhere)
| Kind | Name |
|---|---|
| Stack / region / stage | `pact-dev` / `us-east-1` / `dev` |
| DynamoDB table | `pact-dev` (keys `PK`, `SK`; TTL attribute `ttl`) — local: `pact-local` |
| Secret | `pact/dev/token-signing-key` (template-generated, 64 alphanumerics) |
| Cognito | pool `pact-dev-users`, client `pact-dev-web` (no secret, SRP) |
| Layer | `PactCoreLayer` → Python package `pact_core` |
| Functions (logical IDs) | `ApiFunction`, `AuthorizerFunction`, `ExplainFunction`, `BookingFunction`, `AccountTokenFunction`, `AgentWorkerFunction` |
| HTTP API / authorizers | `PactHttpApi` / `PactTokenAuthorizer` (Lambda, header `x-pact-token`, TTL 0), `CognitoAuthorizer` (JWT) |
| Routes | `GET /v1/health` · `POST /v1/challenges` · `POST /v1/challenges/{challengeId}/answers` · `GET /v1/stats` · `POST /v1/agent-runs` · `GET /v1/agent-runs/{runId}` · `POST /v1/tokens/account` · `POST /v1/demo/bookings` · `POST /v1/authz/explain` · `POST /v1/handoffs` · `GET /v1/handoffs/{handoffId}` |
| Headers | `x-pact-token` (humanity token) · `Authorization: Bearer <Cognito ID token>` · `x-pact-cohort` (analytics label) · `x-pact-poll-key` (handoff poll) |
| Public name / codename | **ARHV** (Agent-Resistant Human Verification) in UI, README, video, writeup / `pact` in code |
| Challenge families | `mdg-v1` (motion-defined glyph, T0 perceptual) · `imu-v1` (phone tilt path, T1 physical) · reserved: `imu-attested`, `hinge-v1`, `presence-v1` |
| imu trace sample | `[t_ms, beta, gamma, alpha\|null, gx, gy, gz, rAlpha, rBeta, rGamma]` (0.1 precision, ≤ 4,000 samples) |
| imu failure reasons | `binding`, `size`, `format`, `timing`, `continuity`, `gravity`, `tilt`, `gyro`, `targets` |
| Token claims | `iss=pact`, `aud=pact-demo`, `sub`, `jti`, `iat`, `nbf`, `exp` (iat+120), `asr` (`motion`\|`physical`\|`account`), `cid` (challenge id; motion and physical), `prf` (proof family, e.g. `imu-v1`) |
| Assurance levels | `motion`, `physical`, `account` (reserved: `physical-attested`, `presence`) |
| Cedar | namespace `Pact`; entities `Pact::Visitor{assurance}`, `Pact::Counter{kind}`; action `Pact::Action::"BookTicket"`; resource id `rush-hour-counter`; policy ids `permit-motion-book`, `permit-physical-book`, `permit-account-book-with-quota`, `forbid-token-replay` |
| Cohorts | `public` (default) · `study` (known humans via `?cohort=study`) · `agent:<alias>:k<K>` (e.g. `agent:nova-2-lite:k4`) · `agent:imu-sim:k0` (sensor spoofs/simulator) · `local` |
| ID formats | `ch_<24 hex>` challenge · `run_<24 hex>` agent run · `bk_<24 hex>` booking · `ho_<24 hex>` handoff · `v_<16 hex>` anonymous visitor sub · handoff keys: 32 hex |
| S3 keys | `runs/<runId>/r<round>_f<frame>.png` (lifecycle: 7 days) |
| Env vars (cloud) | `STAGE`, `TABLE_NAME`, `TOKEN_SECRET_ARN`, `ARTIFACTS_BUCKET`, `WORKER_FUNCTION_NAME`, `AGENT_MODELS`, `AGENT_RUNS_DAILY_CAP`, `BEDROCK_REGION` |
| Env vars (local only; empty in cloud) | `PACT_DDB_ENDPOINT`, `PACT_TOKEN_SECRET`, `PACT_LOCAL_DEV` |
| Frontend env | `VITE_API_URL`, `VITE_REGION`, `VITE_USER_POOL_ID`, `VITE_USER_POOL_CLIENT_ID`, `VITE_STAGE` |
| Model aliases (default) | `nova-2-lite=us.amazon.nova-2-lite-v1:0`, `nova-pro=us.amazon.nova-pro-v1:0` (+ `claude=<profile id>` if enabled in Phase 0) |
| Log event names | `challenge_created`, `challenge_answered`, `imu_verified`, `token_minted`, `authz_decision`, `booking_created`, `account_token_minted`, `handoff_created`, `handoff_verified`, `handoff_delivered`, `agent_run_queued`, `agent_round`, `agent_run_done`, `agent_run_error` |
| DynamoDB item prefixes | `CH#`, `STATS#<family>`, `JTI#`, `QUOTA#`, `BOOKING#`, `RUN#`, `LIMIT#agent-runs`, `HO#` |
| Frontend routes | `/` · `/phone` · `/lab` · `/about` · `/account` |

## 5. Repository layout (file level)
```
backend/
  template.yaml                  # SAM (reference: docs/reference/scaffold/backend/template.yaml; cfn-lint clean)
  samconfig.toml                 # stack pact-dev, us-east-1, use_container build, CORS origins
  env.local.json / env.localstack.json   # sam local overrides (dummy secret, local endpoints)
  requirements-dev.txt
  layers/core/requirements.txt   # PyJWT
  layers/core/pact_core/
    __init__.py
    mdg.py        # generator (reference, tested)
    imu.py        # imu-v1: challenge generator + physics verifier (tested, 21 tests)
    png.py        # stdlib PNG renderer for agent frames (reference, tested)
    tokens.py     # mint/verify HS256 tokens (reference, tested)
    config.py     # env + constants
    keys.py       # token secret: PACT_TOKEN_SECRET (local) or Secrets Manager (cached)
    ids.py        # id generation + validation regexes
    store.py      # all DynamoDB access (single table)
    stats.py      # Wilson intervals, cohort summaries
    http.py       # router, JSON responses, errors, request parsing
    log.py        # structured logging helper
  functions/api/app.py                      # router: health, challenges (mdg-v1 + imu-v1), answers, stats, handoffs, agent-runs
  functions/authorizer/app.py               # handler (authorizer) + explain_handler
  functions/authorizer/authz.py             # Cedar decision (reference, tested)
  functions/authorizer/cedar/schema.cedarschema, policies.cedar   # (reference, validated)
  functions/authorizer/requirements.txt     # cedarpy==4.12.0
  functions/booking/app.py
  functions/account_token/app.py
  functions/agent_worker/app.py
  functions/agent_worker/pact_agent/{models,prompts,solver}.py      # (reference, tested with fake model)
  functions/agent_worker/requirements.txt   # strands-agents>=1.56,<2
  tests/conftest.py, test_mdg.py, test_imu.py, test_authz.py, test_agent.py (reference) + test_store.py, test_api.py,
        test_authorizer.py, test_booking.py, test_account_token.py, test_worker.py (you write)
frontend/  (see docs/FRONTEND.md)
redteam/__init__.py, imu_sim.py (synthetic phone + spoofs), bench.py, report.py, flow_solver.py (stretch)
scripts/doctor.sh, stack_output.py, write_frontend_env.py, bootstrap_amplify.py, deploy_frontend.py,
        local_bootstrap.py, cedar_demo.py, imu_attack_demo.py, gen_shapes_ts.py, make_viz.py, smoke.py (you write)
local/docker-compose.yml
eval/results/*.jsonl, eval/report.md
docs/assets/screenshot-vs-motion.png, shape-icons.png, architecture.png (optional export)
```

## 6. Design decisions (summary; details in the topic docs)
| Decision | Why | Rejected alternatives |
|---|---|---|
| Physical proof (`imu-v1`) as the headline family, verified server-side with cross-sensor physics | Digital-only tests are a capability race; a fresh physical gesture is different evidence. Checking gravity magnitude, tilt-vs-gravity, gyro-vs-orientation and timing rejects cheap spoofs; the remaining gap (physics-aware simulators) is exactly what vendor attestation closes | Trusting a client "done" flag (trivially forged); orientation-only checks (DevTools emulation passes); storing traces for ML scoring (privacy, fingerprinting) |
| Targets public, security from freshness + physics | The targets *are* the instructions; a nonce + random path defeats replay | Hidden targets (the user must see where to tilt) |
| Motion-defined glyph as the perceptual family (T0) | Information-theoretic: single frames are uniform noise, so it's not "VLMs are bad at X today" but "the answer isn't in the screenshot" | Drag-to-target (answer path leaks to the client), static illusions (VLMs improving fast), click-order puzzles (scriptable via pixels) |
| Server sends dot coordinates, not video | Tiny, deterministic, canvas-rendered; no media pipeline. Security-equivalent to pixels (a bot can extract dots from pixels trivially) | Server-rendered GIF/MP4 (needs Pillow/ffmpeg in Lambda, bigger payloads) |
| Keyed SHAKE-256 RNG | Published dots can't be used to reconstruct generator state | `random.Random` (MT19937 state recovery) |
| Cedar in-Lambda via cedarpy | Same policy files for Build It (local) and Ship It (cloud); ABAC with forbid-overrides-permit; testable in pytest | Hand-written if/else (not "authorization as policy"); Amazon Verified Permissions (extra setup, second copy of policies) |
| HTTP API + Lambda authorizer with caching off | Single-use tokens must never be cached; cheaper and simpler than REST API | REST API + WAF (WAF can't attach to HTTP APIs anyway) |
| Async red-team worker | Bedrock calls with images take 2–20 s; HTTP API times out at 30 s; polling shows live progress | Synchronous call (timeouts), Step Functions (more moving parts for the same result) |
| One DynamoDB table, on-demand, TTL | Few access patterns, zero ops, scales to zero, pennies | Multiple tables; RDS |
| Functions split by trust boundary; one router function for the public API | Least privilege where it matters; fewer cold starts elsewhere | One Lambda per route (more boilerplate), one Lambda for everything (authorizer + worker privileges mixed) |
| arm64 + `sam build --use-container` | ~20% cheaper; correct manylinux aarch64 wheels (cedarpy, pydantic-core) | x86_64 (documented fallback if builds misbehave) |
| Amplify Hosting manual (zip) deploys via script | Fully scriptable by Claude Code; no GitHub OAuth dance | Git-connected CI (optional later: nicer push-to-deploy story) |
| DynamoDB Local as default local data plane | No account needed; LocalStack now requires an auth token | LocalStack-only |

## 7. Cost model (us-east-1; verify prices on the AWS pricing pages before quoting in the writeup)
| Item | Per unit | Weekend estimate |
|---|---|---|
| Lambda (arm64) | ~0.3 s × 1 GB per challenge | ≪ $0.01 per 1,000 challenges; free-tier eligible |
| API Gateway HTTP API | ~$1 per million requests | ≈ $0 |
| DynamoDB on-demand | ~6 writes + 2 reads per verification | ≈ $0 |
| S3 | frames of agent runs (~12 PNGs × ~5 KB each) | ≈ $0 |
| Secrets Manager | 1 secret, prorated monthly fee + API calls (cached per container) | < $0.05 |
| Cognito | Essentials free tier covers demo MAUs | $0 |
| Amplify Hosting | small static site | ≈ $0 |
| Bedrock (red team) | Nova 2 Lite: a few thousand input tokens per round | cents for hundreds of runs; Claude-class models are the main cost, so keep N small |
**Writeup line:** "A verification costs a fraction of a cent to serve; the whole weekend, including hundreds of
red-team runs, cost $X (Billing console screenshot)." Take the real number from the Billing console in Phase 6.

## 8. Performance budgets
- Challenge generation ≤ 0.5 s at 1 GB Lambda (≈ 0.1 s locally). Payload ≈ 170 KB JSON (3 rounds × 36 frames × ~600 dots).
- `imu-v1`: challenge < 1 KB; trace ≈ 20 KB for a 5 s tilt (≤ 250 KB at the 4,000-sample cap); `imu.verify` ≈ 5 ms.
- Answer + token ≤ 300 ms warm. Authorizer + booking ≤ 400 ms warm.
- Agent run: 3 rounds × (2–15 s) depending on model; worker timeout 180 s.
- Frontend: first render < 2 s on 4G; Amplify UI (auth) is lazy-loaded so the main bundle stays small.
