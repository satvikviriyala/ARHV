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
Already in the scaffold (keep green): `test_mdg.py` (8), `test_authz.py` (8), `test_agent.py` (4).
Write these (use `from conftest import load_handler`, `moto.mock_aws`, create the table in a fixture with the same
key schema, set env `TABLE_NAME`, `PACT_TOKEN_SECRET`, `STAGE=test`):
| File | Must cover |
|---|---|
| `test_store.py` | consume once → second consume raises AlreadyUsed; expired raises Expired; missing raises NotFound; `mark_jti_used` True then False; quota incr/get; agent cap stops at cap; stats ADD accumulates |
| `test_api.py` | create → 201 and response has no `answers/specs/seed`; answer with real answers (read from table) → pass + token that verifies; wrong answers → pass false + roundsCorrect; 404/409/410/400 paths; stats reflect attempts; cohort header sanitised; unknown route → 404; agent-runs 501 when `PACT_LOCAL_DEV=1` |
| `test_authorizer.py` | missing/garbage/expired/wrong-key token → deny; fresh motion token → allow + context; replay → deny with `forbid-token-replay`; account 1 → allow, 2 → deny; exception inside → deny; template has `ReauthorizeEvery: 0` |
| `test_booking.py` | returns 201 with policy + assurance; account path increments quota |
| `test_account_token.py` | claims → token asr=account; unverified email → 403; no claims + LOCAL_DEV → local-dev-user; no claims otherwise → 401 |
| `test_worker.py` | with a fake Strands model (see `test_agent.py`) + moto S3/DynamoDB: run goes queued → running → done; frames uploaded; stats cohort `agent:<alias>:k4`; model error → status error and **no** stats |
| `test_quota_sync.py` | `config.ACCOUNT_DAILY_QUOTA` equals the literal in `policies.cedar` |

## 3. Frontend tests (Vitest)
`lib/mdg.test.ts` (scaffold) + `cohort.test.ts`, `api.test.ts`, `PactWidget.test.tsx` (see docs/FRONTEND.md §12).

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
10. (cloud only, Phase 3+) `POST /v1/agent-runs {"model": <first alias>, "frames": 1}` → 202; poll until done/error
    (≤ 120 s); require `done`; frames have presigned URLs. Skip with `--no-agent`.

## 5. Manual checks (write results into MEMORY.md › Log)
- Phone (real device) on the Amplify URL: widget fits, animation smooth, options tappable.
- Keyboard only: complete the widget with Tab/1–6/Enter. Screen reader announces rounds (VoiceOver/NVDA quick pass).
- `prefers-reduced-motion` on (OS setting): no autoplay; account path offered.
- DevPanel shows claims and explain result; CloudWatch shows `authz_decision` lines.

## 6. Gates per phase (the phase files repeat these)
| Phase | Gate |
|---|---|
| 0 | `make test-backend` 20 passed; `npm run build` OK; doctor OK; Bedrock converse OK or fallback logged |
| 1 | all backend tests green; `sam validate --lint` OK; deployed; `make smoke SMOKE_ARGS=--no-agent` green |
| 2 | frontend tests + lint green; live URL M1 manual check; `make smoke` still green |
| 3 | `test_worker.py` green; Lab run done with a Bedrock model; smoke step 10 green |
| 4 | account path manual check (deployed); `make local-smoke` green; Ollama bench N ≥ 5 recorded |
| 5 | `eval/report.md` generated from real files; all tests + lint green; security checklist ticked |
| 6 | compliance checklist ticked; submission confirmed |

## 7. Optional CI (only if Phase 5 has time)
`.github/workflows/ci.yml`: on push → setup Python 3.12 + Node 22 → `pip install -r backend/requirements-dev.txt` →
`pytest -q backend/tests` → `ruff check` → `cd frontend && npm ci && npm run lint && npx vitest run && npm run build`.
A green badge in the README helps "Execution".
