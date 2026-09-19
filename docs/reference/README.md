# Reference scaffold: validated starting code

`docs/reference/scaffold/` mirrors the repo root. **Phase 0 copies it into place** without overwriting anything:
```bash
cp -Rn docs/reference/scaffold/. .
```
Everything here was written during the event (Sept 19, 2026) and checked before handover. Keep this folder as the
spec (ruff and pytest exclude it); edit the copies, not these originals.

## What's inside and how it was verified
| Path (relative to repo root after copying) | What | Verified |
|---|---|---|
| `Makefile`, `pyproject.toml` | Canonical commands; ruff + pytest config | `make -n` on all targets; ruff clean |
| `backend/template.yaml` | Full SAM template (all 6 functions, layer, HTTP API with Lambda + JWT authorizers, table, secret, bucket, Cognito) | **cfn-lint 1.57 clean**; SAM translation inspected (authorizer permission, TTL 0, JWT config) |
| `backend/samconfig.toml` | Stack `pact-dev`, us-east-1, container builds, CORS param, `sam local` defaults | parsed (tomllib) |
| `backend/env.local.json`, `env.localstack.json` | `sam local` overrides (dummy secret, local endpoints) | JSON valid |
| `backend/requirements-dev.txt` | Dev deps | installed on Python 3.12 |
| `backend/layers/core/pact_core/mdg.py` | Motion-defined glyph generator (KeyedRng/SHAKE-256) | 8 tests; no-leak z-test; ~0.1 s per challenge |
| `backend/layers/core/pact_core/png.py` | Stdlib PNG renderer (agent screenshots) | valid PNG test |
| `backend/layers/core/pact_core/tokens.py` | HS256 humanity tokens (PyJWT 2.14) | round-trip, tamper, expiry, wrong-key tests |
| `backend/functions/authorizer/authz.py` + `cedar/` | Cedar decision via cedarpy 4.12.0 (dict-form requests; @id mapping) | schema validation passes; 6-case decision table test |
| `backend/functions/*/requirements.txt` | Per-function deps | — |
| `backend/functions/agent_worker/pact_agent/` | Strands red-team agent: models, prompt, solver | fake-model tests on strands-agents 1.56.0 (images reach the model; repair turn; parsing) |
| `backend/tests/` | conftest (sys.path + `load_handler`) + 20 tests | **20 passed** |
| `frontend/` | Vite 8 + React 19 + TS 6 + Tailwind 4 skeleton, **package-lock.json**, eslint/tsconfig/vite config, `lib/mdg.ts` decoder, generated `lib/shapes.ts` | `npm run build`, `npm run lint`, `vitest` (2 tests) pass; Amplify Authenticator import builds |
| `redteam/__init__.py` | Package marker so `make lint` works before Phase 3 | ruff clean |
| `local/docker-compose.yml` | DynamoDB Local (profile `ddb`) / LocalStack (profile `localstack`) on network `pact-local` | `docker compose config` OK for both profiles |
| `scripts/doctor.sh` | Toolchain check | bash -n; dry run |
| `scripts/stack_output.py`, `write_frontend_env.py` | Stack outputs → frontend env | moto CloudFormation test |
| `scripts/local_bootstrap.py` | Create local table (idempotent) | tested against a moto server |
| `scripts/cedar_demo.py` | Cedar decision table | runs |
| `scripts/gen_shapes_ts.py` | Regenerates `shapes.ts`; fails if icon/shape IoU < 0.97 | all 8 shapes IoU ≥ 0.999; output reproducible |
| `scripts/make_viz.py` | Screenshot-vs-motion figure | runs (`docs/assets/screenshot-vs-motion.png`) |
| `scripts/bootstrap_amplify.py`, `deploy_frontend.py` | Amplify app + manual zip deploy | **compile only: not testable offline** (moto lacks Amplify). Verify on first use; fallbacks in docs/AWS_INFRA.md §5 |

## Not in the scaffold (you write these; specs in the docs)
`pact_core/{config,keys,ids,store,stats,http,log}.py` · all `functions/*/app.py` · remaining backend tests ·
`scripts/smoke.py` · `redteam/{bench,report}.py` · the real frontend app (pages/components) · README (final) ·
`eval/report.md` · LICENSE.
