# TESTING — pyramid, commands, smoke test, per-phase gates

## 1. Commands
| What | Command |
|---|---|
| Backend unit + policy + generator tests | `make test-backend` (= `.venv/bin/python -m pytest -q backend/tests`) |
| Frontend unit tests | `make test-frontend` (= `npx vitest run`) |
| Lint / types | `make lint` (ruff check + format check, eslint, `tsc -b`) |
| Template | `cd backend && sam validate --lint` |
| Cloud end-to-end | `make smoke` |
| Local end-to-end | `make local-smoke` |

## 2. Backend tests (pytest + moto; no network, no AWS)
Already in the repo (keep green): `test_mdg.py` (8), `test_imu.py` (21), `test_authz.py` (11), `test_agent.py` (4).
`test_imu.py` includes `test_physically_consistent_synthetic_trace_passes_documenting_the_attestation_gap`: it must
keep passing (it is the honest statement of the web tier's limit, not a bug).
Write these (use `from conftest import load_handler`, `moto.mock_aws`, create the table in a fixture with the same
key schema, set env `TABLE_NAME`, `PACT_TOKEN_SECRET`, `STAGE=test`):
| File | Must cover |
|---|---|
| `test_store.py` | consume once → second consume raises AlreadyUsed; expired raises Expired; missing raises NotFound; `mark_jti_used` True then False; quota incr/get; agent cap stops at cap; stats ADD accumulates |
| `test_api.py` | **imu-v1:** create with `{"family":"imu-v1"}` → 201 with nonce (32 hex) + 3 targets and no `seedHex`; answer with `redteam.imu_sim.physical_trace(challenge, cid)` → pass + token with `asr=physical`, `prf=imu-v1`; `orientation_only_spoof` → `passed:false` and `"gravity" in reasons`; second submit → 409; `{"family":"x"}` → 400 `bad_family`; trace to an mdg challenge → 400 `wrong_family`; body > 512 KB → 400 `too_large`; stats `?family=imu-v1` counts it. **mdg-v1:** create → 201 and response has no `answers/specs/seed`; answer with real answers (read from table) → pass + token that verifies; wrong answers → pass false + roundsCorrect; 404/409/410/400 paths; stats reflect attempts; cohort header sanitised; unknown route → 404; agent-runs 501 when `PACT_LOCAL_DEV=1` |
| `test_authorizer.py` | missing/garbage/expired/wrong-key token → deny; fresh motion token → allow + context; fresh physical token → allow via `permit-physical-book`; replay → deny with `forbid-token-replay`; account 1 → allow, 2 → deny; exception inside → deny; template has `ReauthorizeEvery: 0` |
| `test_booking.py` | returns 201 with policy + assurance; account path increments quota |
| `test_account_token.py` | claims → token asr=account; unverified email → 403; no claims + LOCAL_DEV → local-dev-user; no claims otherwise → 401 |
| `test_worker.py` | with a fake Strands model (see `test_agent.py`) + moto S3/DynamoDB: run goes queued → running → done; frames uploaded; stats cohort `agent:<alias>:k4`; model error → status error and **no** stats |
| `test_quota_sync.py` | `config.ACCOUNT_DAILY_QUOTA` equals the literal in `policies.cedar` |

## 3. Frontend tests (Vitest)
`lib/mdg.test.ts` + `lib/imu.test.ts` (in the repo) + `cohort.test.ts`, `api.test.ts`, `reasons.test.ts`,
`PactWidget.test.tsx` / `PhysicalWidget.test.tsx` if time (see docs/FRONTEND.md §12–13).

## 4. Smoke test spec (`scripts/smoke.py`, you write it in Phase 1)
Args: `--api URL` (required), `--stack`, `--region`, `--local`, `--profile ddb|localstack`. Uses only stdlib
`urllib` + boto3. Exit code 0 only if every check passes; print one line per check.
1. `GET /v1/health` → 200 `ok: true`.
2. `POST /v1/challenges` (cohort `local` if `--local`, else `public`) → 201; keys include `challengeId`, 3 rounds with
   6 options and `frameCount`; body must **not** contain `"answers"`, `"specs"`, `"seed"`.
3. Wrong answers → 200 `passed: false`.
4. New challenge; **read the true answers from DynamoDB** with the developer's credentials (`TableName` output, or
   `pact-local` + local endpoint with `--local`) (a test-only path that doesn't exist in the public API) → submit →
   200 `passed: true` + token.
5. Re-submit the same challenge → 409.
6. `POST /v1/demo/bookings` without header → 401. With `x-pact-token: garbage` → 403.
7. With the valid token → 201 and `policy == "permit-motion-book"`.
8. Same token again → 403. `POST /v1/authz/explain` with it → `decision: DENY`, policies contain `forbid-token-replay`.
9. `GET /v1/stats` → cohort present with attempts ≥ 2.
9b. **imu (physical):** `POST /v1/challenges {"family":"imu-v1"}` → 201 (nonce, 3 targets) → answer with
    `redteam.imu_sim.physical_trace(ch, cid)` → 200 `passed: true`, `assurance: "physical"` → booking → 201 with
    `policy == "permit-physical-book"` → replay → 403 → explain → `DENY` + `forbid-token-replay`. Then a fresh challenge
    answered with `orientation_only_spoof` → `passed: false` with `gravity` in `reasons`. (smoke.py imports
    `redteam.imu_sim`; add the repo root to `sys.path`.)
10. (cloud only, Phase 3+) `POST /v1/agent-runs {"model": <first alias>, "frames": 1}` → 202; poll until done/error
    (≤ 120 s); require `done`; frames have presigned URLs. Skip with `--no-agent`.

## 5. Manual checks (write results into MEMORY.md › Log)
- Phone (real device) on the Amplify URL: widget fits, animation smooth, options tappable.
- **Tilt check on a real iPhone (Safari) and, if available, an Android phone (Chrome):** permission prompt appears on
  tap (iOS), the dot follows the tilt, rings fill, pass → booking `permit-physical-book`. Log the `metrics`
  (`tiltErrDeg`, `gyroCorr`, `gravityFrac`, `medianDtMs`, `gravitySign`) of each device in MEMORY.md › Metrics:
  they are real-device evidence for the README. A failure → tuning procedure in docs/PHYSICAL.md §3.
- Keyboard only: complete the widget with Tab/1–6/Enter. Screen reader announces rounds (VoiceOver/NVDA quick pass).
- `prefers-reduced-motion` on (OS setting): no autoplay; account path offered.
- DevPanel shows claims and explain result; CloudWatch shows `authz_decision` lines.

## 6. Gates per phase (the phase files repeat these)
| Phase | Gate |
|---|---|
| 0 | `make test-backend` 20 passed; `npm run build` OK; doctor OK; Bedrock converse OK or fallback logged |
| 1 | all backend tests green; `sam validate --lint` OK; deployed; `make smoke SMOKE_ARGS=--no-agent` green incl. step 9b (imu) |
| 2 | frontend tests + lint green; live URL M1 manual check incl. a real-phone tilt pass; `make smoke` still green |
| Sprint | `docs/phases/PHASE_SPRINT_TO_2000.md §4` gate |
| 3 | `test_worker.py` green; Lab run done with a Bedrock model; smoke step 10 green |
| 4 | account path manual check (deployed); `make local-smoke` green; Ollama bench N ≥ 5 recorded |
| 5 | `eval/report.md` generated from real files; all tests + lint green; security checklist ticked |
| 6 | compliance checklist ticked; submission confirmed |

## 7. Optional CI (only if Phase 5 has time)
`.github/workflows/ci.yml`: on push → setup Python 3.12 + Node 22 → `pip install -r backend/requirements-dev.txt` →
`pytest -q backend/tests` → `ruff check` → `cd frontend && npm ci && npm run lint && npx vitest run && npm run build`.
A green badge in the README helps "Execution".
