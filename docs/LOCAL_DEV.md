# LOCAL DEV — the Build It track (everything on localhost, no AWS account needed)

Goal for the video (≈ 25 s): *"The same code runs on my laptop: SAM CLI emulates API Gateway + Lambda (including
the Cedar authorizer), DynamoDB runs locally, and a Strands agent on a local Ollama vision model fails the same
puzzle."* Tools shown: **SAM CLI, Cedar, Strands Agents, DynamoDB Local (or LocalStack), Ollama**.

## 1. Pieces
| Piece | Local stand-in | How |
|---|---|---|
| API Gateway + Lambdas + Lambda authorizer | `sam local start-api` (Docker) | `make local-api` → http://127.0.0.1:3000 |
| DynamoDB | **DynamoDB Local** (`amazon/dynamodb-local`, default) or LocalStack (needs `LOCALSTACK_AUTH_TOKEN`) | `make local-up [LOCAL_PROFILE=localstack]` |
| Secrets Manager | `PACT_TOKEN_SECRET` dummy value in `backend/env.local.json` | automatic |
| Cognito JWT authorizer | not emulated by SAM (skipped); `PACT_LOCAL_DEV=1` makes `/v1/tokens/account` mint for `local-dev-user` | automatic |
| Bedrock red team | Strands + **Ollama** via the bench CLI (the cloud worker isn't used locally; `/v1/agent-runs` → 501) | `make bench BACKEND=ollama …` |
| Cedar | cedarpy in the local authorizer container + `make cedar-demo` | automatic |

## 2. Step by step
```bash
make local-up                         # DynamoDB Local on :8000 + table pact-local (network pact-local)
make local-api                        # sam build + sam local start-api --docker-network pact-local --env-vars env.local.json
make local-smoke                      # same smoke test as the cloud, against http://127.0.0.1:3000
(cd frontend && ../.venv/bin/python ../scripts/write_frontend_env.py --local && npm run dev)   # UI on :5173 against local API
make cedar-demo                       # decision table from the real policy files
ollama pull qwen2.5vl:7b              # or llama3.2-vision:11b / gemma3:4b (pick by RAM; must list "vision" in `ollama show`)
make bench BACKEND=ollama MODEL=qwen2.5vl:7b K=4 N=10 API=http://127.0.0.1:3000
make local-down
```
Notes:
- `write_frontend_env.py --local` needs the cloud stack for the Cognito ids. If the stack isn't deployed yet, write
  `frontend/.env.development.local` by hand with `VITE_API_URL=http://127.0.0.1:3000` and placeholder pool ids
  (the account page won't work locally anyway).
- First `sam local` request per function cold-starts a container (5–15 s); `--warm-containers LAZY` keeps them warm.
- The Lambda containers reach DynamoDB Local at `http://dynamodb-local:8000` because both are on the Docker network
  `pact-local` (see `local/docker-compose.yml`, `backend/env.local.json`). LocalStack profile: `env.localstack.json`
  → `http://localstack:4566`.

## 3. LocalStack (optional)
Since March 23, 2026 the LocalStack image needs a free account + `LOCALSTACK_AUTH_TOKEN` (free for non-commercial
use and verified students). Human step H8: sign up, `export LOCALSTACK_AUTH_TOKEN=…`, then
`make local-up LOCAL_PROFILE=localstack && make local-api LOCAL_PROFILE=localstack`. If the container logs a
licence/auth error, fall back to the default DynamoDB Local profile. The Build It story is identical.

## 4. Troubleshooting
| Symptom | Cause → fix |
|---|---|
| `Could not connect to the endpoint URL: http://dynamodb-local:8000` | `sam local` not on the network → use `make local-api` (passes `--docker-network pact-local`); `docker network ls` should list `pact-local`; run `make local-up` first |
| `ResourceNotFoundException` table | table missing (DynamoDB Local is in-memory; restart = empty) → `make local-up` recreates it |
| 500 from authorizer locally | cedarpy wheel/arch mismatch in the container → `sam build --use-container` (default via samconfig) |
| Account route returns 401 locally | `PACT_LOCAL_DEV` not "1" → check `backend/env.local.json` and that the var is declared in the template |
| Ollama reply isn't JSON | expected sometimes; the solver repairs once, then scores it invalid. Try a stronger local model |
| Very slow Ollama | use `gemma3:4b`, K=1 or 4, N=5 for the video beat |
