# RISKS AND FALLBACKS — decide fast, log it, keep the critical path moving

| # | Risk | Trigger (how you know) | Fallback (do this) |
|---|---|---|---|
| R1 | Deadline earlier than assumed | Schedule page/Discord shows a time before Sun 23:59 | Apply `PLAN.md › Compression`; submit early at M1 or M2 |
| R2 | AWS credentials/account not ready | `aws sts get-caller-identity` fails | Human step H2. Meanwhile do Phase 1 code + moto tests and the Phase 2 UI against `sam local` |
| R3 | Bedrock model not callable | `converse` → AccessDenied / ValidationException | Nova: use `us.`/`global.` profile id. Claude: drop the alias until form H4 is approved. All Bedrock down: Lab uses a pre-recorded run + Ollama bench for the live demo; say so |
| R4 | `sam build` fails (wheels, arch, Docker) | pip/cedarpy/pydantic-core errors | Docker running? → `sam build --use-container` (default) → switch to x86_64 (Globals + layer) → log |
| R5 | Deploy fails | CloudFormation `ROLLBACK_COMPLETE` | Read `aws cloudformation describe-stack-events --stack-name pact-dev` (first FAILED event). Stack in ROLLBACK_COMPLETE on first create must be deleted before retrying → **ask the human** to run `sam delete` |
| R6 | Reserved concurrency / quota errors | "UnreservedConcurrentExecution below minimum" | Remove any `ReservedConcurrentExecutions`; keep bench concurrency ≤ 3 |
| R7 | CORS errors in browser | Console: "blocked by CORS policy" | Exact origin in `AllowedOrigins` (scheme+host, no slash), header listed in `AllowHeaders`, redeploy backend |
| R8 | Humans fail the puzzle | Pilot: any human fails twice, or round accuracy < 90% | `docs/CHALLENGE_MDG.md §7` easing knobs (NOISE ↓, radius ↑, FRAMES ↑), icons legible, hint text |
| R9 | An agent scores above chance | Round-accuracy lower CI > 0.25 | §7 hardening knobs, re-run human pilot. If still above chance, report honestly and reframe (EVALUATION §7) |
| R10 | Amplify deploy script fails | 403 on upload / job FAILED | Script retries without Content-Type → console drag-and-drop of `dist` zip (human, 2 min) |
| R11 | Cognito/Authenticator eats time | > 60 min in Phase 4 without a working sign-in | Minimal custom form using `aws-amplify/auth` `signUp/confirmSignUp/signIn`, or cut to "backend + Cedar quota shown via explain" and show it in the video |
| R12 | LocalStack auth token unavailable | Container exits with licence error | Default `LOCAL_PROFILE=ddb` (DynamoDB Local). Story unchanged |
| R13 | Ollama too slow / no vision model | > 60 s per round or model lacks vision | `gemma3:4b`, K=1, N=5 for the Build It beat |
| R14 | Payload too slow on mobile | Challenge load > 3 s on 4G | FRAMES 36→24, N_DOTS 600→450 (re-run tests; tests use constants) |
| R15 | Credits/cost spike | Budget email / Billing shows > $10 | Stop the matrix; Nova only; lower `AgentRunsDailyCap` via parameter override |
| R16 | Scoreboard polluted by testers | `public` cohort noisy | Only `study` counts for H1; builders never use `?cohort=study` |
| R17 | Time overrun | Behind `PLAN.md` by > 1 h at a phase boundary | Cut list in order; never cut M1, M2, video, writeup, submission |
| R18 | Video over 3:00 | Edit timeline > 2:58 | Speed up the widget segment ×1.5, drop console cuts to 2 s each, trim Build It to 15 s |
| R19 | Claude Code session loses context | New session / compaction | SessionStart hook re-injects MEMORY.md; re-read the current phase file; continue from Next Steps |

## Escalation rule
3 failed fix attempts on one issue → write an Open Issue in MEMORY.md (error, attempts, chosen fallback) → apply the
fallback → move on. Ask the human only with a precise question and the exact command you need them to run.
