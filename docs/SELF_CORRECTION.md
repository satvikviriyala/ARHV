# SELF-CORRECTION — how Claude Code handles errors (mandatory)

## 1. The loop
1. **Reproduce** with the smallest command; copy the exact error text (first failing line, not the whole log).
2. **Locate** the root cause: read the failing code and logs (`sam logs -n <Fn> --tail`, CloudWatch, browser
   console/network tab, `describe-stack-events`), then the playbook below. Write the cause in one sentence.
3. **Fix minimally**, addressing the cause. One logical change per attempt.
4. **Verify**: re-run the failing check **and** the phase gate (`docs/TESTING.md §6`).
5. **Record** in `MEMORY.md › Errors & Fixes`: `symptom → cause → fix → verification`. Code bug → add a regression test.

## 2. Guardrails
- Max **3 attempts** per issue; the same error twice means stop and re-read (docs, logs, the library's docs) before
  attempt 3. Then take the fallback in `docs/RISKS_AND_FALLBACKS.md` and log an Open Issue.
- Never make a check pass by weakening it: no skipping tests, no `# noqa` to silence real issues, no disabling the
  authorizer, no `AllowOrigins: *`, no IAM `*` beyond the documented Bedrock statement, no `--no-verify` commits.
- If a change makes things worse, go back to the last green commit (`git stash` / `git revert <sha>`); don't pile fixes.
- Verify claims: don't write "deployed", "passing" or "fixed" until you saw the output that proves it.
- Keep `main` demo-able; for risky refactors use a branch and merge only when the gate is green.
- After context compaction or a new session: re-read `MEMORY.md` (auto-injected) and the current phase file before acting.

## 3. Playbooks (known failure modes)
| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: pact_core` in Lambda | Layer not built/attached or wrong layout | `sam build` → check `.aws-sam/build/PactCoreLayer/python/pact_core/`; Globals `Layers: [!Ref PactCoreLayer]`; layer `Metadata.BuildMethod: python3.12` |
| `ModuleNotFoundError: cedarpy` / `_cedarpy` import error | Wheel for wrong arch/platform | `sam build --use-container`; arm64 everywhere (function + layer) or switch all to x86_64 |
| `sam build` very slow | Emulated arm64 container on Intel | Accept once (cached), or switch to x86_64 and log |
| Protected route always **401** | `x-pact-token` header missing (API GW rejects before the authorizer) | Client must send the header; CORS `AllowHeaders` must include it |
| Protected route always **403** | Authorizer returns deny: bad secret (local vs cloud), clock/exp, replay, wrong response shape | `make logs`; `POST /v1/authz/explain` with the token; response must be `{"isAuthorized": bool, "context": {...}}` with `EnableSimpleResponses: true` |
| Protected route **500** | Authorizer raised/timed out | Check logs; catch-all deny; secret fetch permission (`AWSSecretsManagerGetSecretValuePolicy`) |
| First booking with a fresh token is 403 "replay" | Authorizer invoked twice (caching off is fine) or client retried | Ensure the client doesn't auto-retry POSTs; check logs for two `authz_decision` lines with the same jti |
| DynamoDB `ValidationException: reserved keyword` | `status`/`ttl`/`count` used directly | `ExpressionAttributeNames` |
| `ConditionalCheckFailedException` surfacing as 500 | Not mapped | `consume_challenge` → GetItem → 404/409/410; `mark_jti_used` → return False |
| `Decimal is not JSON serializable` | DynamoDB numbers | `http.ok` uses a default that converts Decimal → int/float |
| Browser CORS error | Origin not allowed / header not allowed / preflight | Fix `AllowedOrigins` param (exact), redeploy; check the Network tab's OPTIONS response |
| Frontend calls `undefined/v1/...` | Vite env missing at build | `make web-env` then rebuild; `config.ts` should fail loudly |
| Deep link 404 on Amplify | SPA rewrite missing | Re-run `make web-bootstrap` (sets the rule) |
| Bedrock `ValidationException: on-demand throughput isn't supported` | Bare model id used | Use the `us.`/`global.` inference profile id |
| Bedrock `AccessDeniedException` | IAM action missing, or Anthropic form not submitted | IAM has both InvokeModel actions; human step H4; remove the alias meanwhile |
| Bedrock `ThrottlingException` | Burst of runs | Retry once with backoff in the solver's caller; lower bench concurrency; runs with errors aren't counted |
| Worker never finishes | Timeout (180 s) or exception | `sam logs -n AgentWorkerFunction`; K=8 with slow models: lower K or raise timeout to 300 s |
| `Task timed out after 30 s` on an API route | Synchronous heavy work | Move it to the worker; the API route only queues |
| Stack `ROLLBACK_COMPLETE` on first create | Previous create failed | Read events; human deletes the stack (`sam delete`) then redeploy |
| `sam local` can't reach DynamoDB | Network or endpoint | `make local-up` first; `make local-api` uses `--docker-network pact-local`; endpoint `http://dynamodb-local:8000` |
| Vitest "document is not defined" | Wrong environment | `test.environment = "jsdom"` in `vite.config.ts` (scaffold has it) |
| ESLint react-refresh warning | Component defined in `main.tsx` | Move components to their own files |
| Stop hook says MEMORY.md is stale | Files changed after the last MEMORY.md update | Update MEMORY.md (Log/Snapshot/Next Steps); the hook blocks only once per state |
