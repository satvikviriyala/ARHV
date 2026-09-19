# AWS INFRA — SAM, deploy, Amplify, Cognito, Bedrock, IAM, logs, cost

Reference template (cfn-lint clean; SAM translation checked): `docs/reference/scaffold/backend/template.yaml`.
Config: `backend/samconfig.toml` (stack `pact-dev`, us-east-1, `use_container` build, CORS origins, `sam local` defaults).

## 1. Prerequisites and credentials
- AWS CLI v2, SAM CLI ≥ 1.100, Docker Desktop running, Python 3.12, Node ≥ 20.19 (22 LTS recommended). `make doctor`.
- Credentials: `aws configure` (access key of an IAM user with admin rights on this personal hackathon account) or
  `aws configure sso`. Default region **us-east-1**. Check with `aws sts get-caller-identity`.
- Never paste keys into chat or files in the repo. Claude Code must not read `~/.aws/credentials` (denied in settings).

## 2. Amazon Bedrock access (Phase 0)
- Serverless models are enabled by default in commercial regions (Oct 2025 change). **Anthropic models need a one-time
  use-case form** (Bedrock console → Model catalog → any Anthropic model → submit). Human step H4.
- Discover callable profiles and smoke-test (commands in `docs/REDTEAM_AGENT.md §2`). Nova 2 Lite must be called via
  `us.amazon.nova-2-lite-v1:0` or `global.amazon.nova-2-lite-v1:0` (no in-region endpoint).
- Put the verified aliases into `samconfig.toml` → `parameter_overrides` → `AgentModels="nova-2-lite=…,nova-pro=…,claude=…"`
  (keep `Stage` and `AllowedOrigins` in the same line). Record them in MEMORY.md › Snapshot.

## 3. What the template creates (and why)
| Resource | Key settings |
|---|---|
| `PactTable` | PK/SK strings, on-demand, TTL `ttl` |
| `TokenSecret` | `GenerateSecretString` 64 chars, no punctuation (nobody ever types or sees it) |
| `ArtifactsBucket` | private, SSE-S3, lifecycle deletes `runs/` after 7 days |
| `UserPool` / `UserPoolClient` | email as username, auto-verified email, no client secret, SRP auth |
| `PactCoreLayer` | `layers/core/` built with `BuildMethod: python3.12`, arm64 |
| `PactHttpApi` | CORS (exact origins), throttling 25 rps / burst 50, `PactTokenAuthorizer` (Lambda, header `x-pact-token`, **ReauthorizeEvery 0**), `CognitoAuthorizer` (JWT: issuer = user pool, audience = client) |
| `ApiFunction` | 1 GB (generation is CPU-bound), routes: health, challenges, answers, stats, agent-runs; can invoke the worker |
| `AuthorizerFunction` / `ExplainFunction` | same code dir; Cedar via cedarpy; secret read; table access (explain: read-only) |
| `BookingFunction` | protected route behind the Lambda authorizer |
| `AccountTokenFunction` | route behind the Cognito JWT authorizer |
| `AgentWorkerFunction` | 1 GB, 180 s, Bedrock `InvokeModel`/`InvokeModelWithResponseStream`, S3 CRUD, table CRUD |
| Globals | Python 3.12, arm64, JSON logging, layer attached, env `STAGE/TABLE_NAME/TOKEN_SECRET_ARN` + local-only vars (empty) |
Outputs: `ApiUrl`, `UserPoolId`, `UserPoolClientId`, `TableName`, `ArtifactsBucketName`, `Region`.
Parameters: `Stage`, `AllowedOrigins` (CommaDelimitedList), `BedrockRegion`, `AgentModels`, `AgentRunsDailyCap`.

## 4. Build and deploy (backend)
```bash
make build     # cd backend && sam validate --lint && sam build   (container build: first run pulls images, 3–8 min)
make deploy    # sam deploy (samconfig) → then scripts/write_frontend_env.py writes frontend/.env.*.local
make smoke     # end-to-end check against the deployed API
```
First deploy ≈ 4–8 min. Subsequent code-only deploys ≈ 1–2 min. If `sam build --use-container` is too slow on an
Intel machine building arm64, switch **both** Globals `Architectures` and the layer's `CompatibleArchitectures` /
`BuildArchitecture` to `x86_64` and log the decision.

## 5. Amplify Hosting (frontend)
```bash
make web-bootstrap   # once: creates app "pact-web" + branch "main" (manual deploys), SPA rewrite rule,
                     # patches samconfig AllowedOrigins with https://main.<appId>.amplifyapp.com → run `make deploy` again
make web-env         # frontend/.env.production.local from stack outputs (public config, not secrets)
make web-deploy      # npm run build → zip dist → CreateDeployment → PUT zip → StartDeployment → poll job
```
`scripts/bootstrap_amplify.py` and `scripts/deploy_frontend.py` are **untested against live AWS** (no Amplify in
moto). If the upload step returns 403 SignatureDoesNotMatch, the script retries without `Content-Type`. Fallback
(2 min, human): Amplify console → app `pact-web` → branch `main` → "Deploy updates" → drag-and-drop a zip of
`frontend/dist` (index.html at the zip root). Optional later: connect the GitHub repo in the console with an
`amplify.yml` (`appRoot: frontend`, `npm ci`, `npm run build`, `baseDirectory: dist`) for push-to-deploy.

## 6. Cognito
- Default Cognito email sender: roughly 50 emails/day, fine for a demo. Sign-up needs a real inbox (code by email).
- Test account for the video: create it in Phase 4 and keep it verified. Don't show the email address on camera.
- The frontend sends the **ID token** (has `email_verified`); API Gateway validates `iss`/`aud` before the Lambda runs.

## 7. Budget alarm (Phase 0; human supplies the email)
Credits pay the bill, so alert on **gross** usage (`IncludeCredit: false`):
```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
aws budgets create-budget --account-id "$ACCOUNT" \
  --budget '{"BudgetName":"pact-weekend","BudgetLimit":{"Amount":"10","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST","CostTypes":{"IncludeCredit":false}}' \
  --notifications-with-subscribers '[{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN","Threshold":50,"ThresholdType":"PERCENTAGE"},"Subscribers":[{"SubscriptionType":"EMAIL","Address":"YOUR_EMAIL"}]}]'
```

## 8. Observability (also video material)
- `make logs` → `sam logs -n AuthorizerFunction --tail` (Cedar decisions live).
- CloudWatch Logs Insights (log group `/aws/lambda/pact-dev-AuthorizerFunction-*`):
```
fields @timestamp, decision, policies, assurance, action, reason, jti
| filter event = "authz_decision"
| sort @timestamp desc
| limit 50
```
- Errors across functions: `fields @timestamp, @log, message | filter level = "ERROR" | sort @timestamp desc | limit 50`
- Agent rounds: `fields @timestamp, runId, model, round, answer, valid, latencyMs | filter event = "agent_round"`
- For the video: DynamoDB console → `pact-dev` → Explore items → `PK = STATS#mdg-v1` shows the counters.

## 9. Cost (see docs/ARCHITECTURE.md §7)
Take the real number for the writeup from Billing → Bills (charges and credits) on Sunday evening. Cost Explorer lags up to 24 h.

## 10. Teardown (after judging only: judges may open the URL)
`cd backend && sam delete --stack-name pact-dev` (human approval required; denied for Claude Code by default).
Then delete the Amplify app in the console. Don't do this before results are announced.

## 11. Gotchas (all hit by someone before, now pre-empted)
- New accounts: Lambda concurrency limit can be **10**. Don't set reserved concurrency; keep bench concurrency ≤ 3.
- HTTP API integration timeout is **30 s**: never do Bedrock calls in API routes.
- `{param}` in YAML flow mappings breaks parsing: keep templated paths **quoted** (the reference template does).
- `sam local` only overrides env vars **declared in the template**: that's why `PACT_*` vars exist with empty values.
- `sam local` skips JWT (Cognito) authorizers; the account route runs unauthenticated locally, so the handler's
  `PACT_LOCAL_DEV` fallback exists. Lambda authorizers *are* emulated locally.
- CORS origin must match exactly (scheme + host, no trailing slash). Preflight is answered by API Gateway.
- Vite env vars are build-time: after `make web-env`, rebuild/redeploy the frontend.
