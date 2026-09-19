# MEMORY.md — live project state (Claude Code keeps this current)

> **Update rules (mandatory):**
> 1. After EVERY task: append to **Log**; refresh **Snapshot** and **Next Steps**.
> 2. Every error: add an **Errors & Fixes** entry (symptom → root cause → fix → verification). Still failing after
>    3 attempts → move to **Open Issues** with the fallback you chose (see docs/RISKS_AND_FALLBACKS.md).
> 3. Every non-obvious choice or deviation from docs → one line in **Decisions** (what — why — alternatives).
> 4. Anything that needs the human → **Human-Blocked** (what, exact command/link, since when). Tell the human.
> 5. Numbers (pass rates, costs, latencies) only from real runs; cite the command/file that produced them.
> 6. Never delete history (you may tick Next Steps). Keep Snapshot ≤ 40 lines. Newest Log entries at the bottom.

## Snapshot
- Deadline: DATE CONFIRMED as Sun 2026-09-20; exact time/timezone UNCONFIRMED — the official schedule says hours are still being finalised
- Current phase: 0 (preflight)
- Milestones: M1 human-pass-live [ ] · M2 AI-fails-live [ ] · Early submission [ ] · Final submission [ ]
- Repo URL: https://github.com/satvikviriyala/ARHV (public; main)
- Web URL (Amplify): — (bootstrap blocked by missing `amplify:ListApps`)
- API URL: —
- Stack: pact-dev (us-east-1) — not deployed
- Bedrock models verified (alias=id): nova-2-lite=us.amazon.nova-2-lite-v1:0; nova-pro=us.amazon.nova-pro-v1:0; Claude unavailable pending H4
- Scaffold: validated reference copied; Phase 0 toolchain, setup, baseline, and Nova smoke green; bootstrap LICENSE/commit pending
- Baseline: backend 20 passed; ruff/format/eslint/tsc clean; frontend build plus 2 tests passed; Cedar 6-row demo and SAM validation passed
- Human pass rate (study cohort): — · Best agent pass rate: —
- Last green commit: 3bf60e4 (`chore(phase-0): record verified preflight`)
- Blockers: H1 exact cutoff/timezone pending · LICENSE holder string needed (Git identity unset) · H4 Claude access pending · Amplify console fallback · H5 budget alarm unverified (`budgets:ViewBudget` denied)

## Next Steps
- [ ] H1: confirm the submission deadline from the schedule, Discord, or email
- [x] Phase 0: install toolchain items and re-run doctor (all required tools present; LocalStack token optional)
- [ ] Phase 0: provide the exact LICENSE copyright-holder string, then finish task 0.3
- [x] Phase 0: run `make setup` (fresh login shell succeeded)
- [x] Phase 0: complete 0.5 baseline gate (all prescribed checks passed)
- [x] Phase 0: complete 0.6 AWS + Bedrock preflight (Nova calls passed; Claude blocked by H4; AgentModels set)
- [ ] Phase 0: complete 0.7 Amplify bootstrap and record URL (blocked; use documented console fallback)
- [ ] Phase 0: complete 0.8 budget-alarm verification (user reports console setup; read-only CLI verification is blocked by missing `budgets:ViewBudget`)
- [x] Phase 0: verify 0.9 existing public GitHub remote (no create/push needed)
- [ ] Phase 0: once H1 is answered, record task 0.1 and continue with task 0.2

## Human-Blocked
- 2026-09-19 — H1: confirm the submission deadline. Open https://www.wemakedevs.org/aws/first-commit/schedule
  (or check Discord/email), then tell Claude Code the exact deadline and timezone. No compression decision can be
  made until this is confirmed.
- 2026-09-19 — [RESOLVED 17:20 IST] Phase 0 toolchain: on macOS run `brew install python@3.12 node awscli
  aws-sam-cli` and install/start Docker Desktop; a fresh login-shell doctor run now passes all required checks.
  LocalStack token remains optional because the default local profile uses DynamoDB Local.
- 2026-09-19 — Phase 0 task 0.3: initialized a new Git repository on `main` and copied the validated reference
  scaffold into the workspace. `git config user.name` is empty; tell Claude Code the exact copyright holder string
  so it can create the MIT LICENSE and make the bootstrap commit.
- 2026-09-19 — [RESOLVED] Phase 0 task 0.4 toolchain blocker: Python 3.12 and the remaining local tools were
  installed; `make setup` was rerun in a fresh login shell and succeeded.
- 2026-09-19 — H4: Claude vision access is pending. In the Bedrock console (us-east-1), open Model catalog,
  select an Anthropic Claude model, and submit the one-time use-case form; do not paste any credentials here.
- 2026-09-19 — Phase 0 task 0.7 Amplify: the current IAM user lacks `amplify:ListApps`. In the AWS Amplify
  console (us-east-1), create `pact-web` with “Deploy without Git”, branch `main`, and the SPA rewrite; record
  `{"appId":"…","branch":"main","url":"https://main.<appId>.amplifyapp.com","region":"us-east-1"}` in
  `.pact/amplify.json`, then tell Claude Code the app id/URL. IAM changes are not requested.
- 2026-09-19 — H5: provide an email for the documented `aws budgets create-budget` command in
  `docs/AWS_INFRA.md §7`, or create the `$10` monthly gross-usage alarm in the AWS Billing console.
- 2026-09-19 — H5: budget alarm needs a human-supplied email. Either provide the email for the command in
  `docs/AWS_INFRA.md §7` or create the `$10` monthly gross-usage alarm in the Billing console.
- 2026-09-19 — LICENSE holder: `git config --show-origin --get-regexp '^user\.(name|email)$'` returned no
  entries; no exact holder string is available. Provide the exact legal name or organization string to place
  after `Copyright (c) 2026`; do not infer it from the machine username, email, or auto-generated commit identity.
- 2026-09-19 — H5 verification: the user reports the `$10` monthly gross-usage alarm was created in the Billing
  console, but the read-only AWS CLI check was denied by missing `budgets:ViewBudget`. No budget facts were
  returned; keep H5 pending until a permitted read-only check or console-visible facts can be supplied without
  sharing an email address.

## Decisions
- 2026-09-19 — Project = PACT (agent-resistant human verification). Primary challenge = motion-defined glyph `mdg-v1`: single frames carry no information, so screenshot agents get noise. Rejected: drag-to-moving-target (target path had to be sent to the client, trivially scriptable).
- 2026-09-19 — us-east-1 (Bedrock model breadth; Nova 2 Lite needs a `us.`/`global.` profile); arm64 Lambdas; one DynamoDB table; HTTP API; functions split by trust boundary (public API / authorizer / protected action / account token / worker).
- 2026-09-19 — Cedar evaluated with `cedarpy` inside the Lambda authorizer, so the same policy files run locally (Build It) and deployed (Ship It). Rejected: Amazon Verified Permissions (more setup, a second copy of the policies).
- 2026-09-19 — Accessible path = Cognito-verified account → token (assurance=account) → Cedar daily quota of 2 (non-cognitive, WCAG 2.2 SC 3.3.8).
- 2026-09-19 — Generator randomness = keyed SHAKE-256 (`KeyedRng`). Rejected: Mersenne Twister, whose state can be recovered from the published dots, which would reveal hidden dots and the mask.
- 2026-09-19 — Local data plane default = DynamoDB Local (no account). LocalStack is optional: it needs a free auth token since March 2026.

## Log
- 2026-09-19 — Handover pack created: docs + validated reference scaffold (backend: 20 pytest tests pass, ruff clean, cfn-lint clean; Cedar policies validated with cedarpy 4.12.0; Strands 1.56.0 plumbing tested with a fake model; frontend skeleton builds/lints/tests on Vite 8 + React 19 + Tailwind 4). No project code written or deployed yet.
- 2026-09-19 — Phase 0 task 0.1 inspected; the official schedule confirms submissions close on Sun 2026-09-20,
  but says the stopping time is still being finalised. Exact time/timezone remains H1; no compression decision made.
- 2026-09-19 — Phase 0 task 0.2 ran `bash docs/reference/scaffold/scripts/doctor.sh`; git passed, but Python 3.12,
  Node/npm, Docker, AWS CLI, and SAM CLI were missing. Ollama, gh, and the LocalStack token were optional warnings.
- 2026-09-19 — Phase 0 task 0.3 initialized `main` and copied the validated reference scaffold; the prescribed
  path check passed. LICENSE and the bootstrap commit remain pending the copyright holder.
- 2026-09-19 — Phase 0 task 0.4 ran `make setup`; it stopped at the missing Python 3.12 interpreter, so baseline
  verification could not start.
- 2026-09-19 — Phase 0 task 0.2 re-run through `zsh -lic 'bash docs/reference/scaffold/scripts/doctor.sh'`;
  all required tools, Docker daemon, AWS credentials, and us-east-1 passed. LocalStack token was the only warning.
- 2026-09-19 — Phase 0 task 0.4 completed with `zsh -lic 'make setup'`: Python dependencies installed and
  `frontend/npm install` added 398 packages with 0 vulnerabilities. npm emitted peer-dependency warnings but
  exited 0; the documented `--legacy-peer-deps` fallback was not used. Baseline gate is next.
- 2026-09-19 — Phase 0 task 0.5 passed every prescribed gate: `make test-backend` = 20 passed;
  `make lint` = ruff/format/eslint/tsc clean; frontend build and Vitest = 2 tests passed; `make cedar-demo`
  printed all 6 decisions; `sam validate --lint` reported a valid SAM template.
- 2026-09-19 — Phase 0 task 0.6 passed AWS identity, profile discovery, Nova 2 Lite, and Nova Pro smoke calls.
  The strongest listed US Claude profile (`us.anthropic.claude-opus-5`) was unavailable to this account.
  `backend/samconfig.toml` now sets the two verified Nova aliases; Claude is intentionally omitted.
- 2026-09-19 — Phase 0 task 0.9 verified the existing `origin` remote and GitHub repository:
  `gh auth status` passed, `gh repo view` reported `isPrivate=false` and default branch `main`.
  No `gh repo create` or push was run.
- 2026-09-19 — Phase 0 task 0.7 `make web-bootstrap` failed before app creation because the AWS user lacks
  `amplify:ListApps`. The documented fallback is a human-created Amplify app `pact-web` via “Deploy without Git”;
  record its app id/URL in `.pact/amplify.json`, then patch `AllowedOrigins`.
- 2026-09-19 — Committed the verified Phase 0 preflight state as `3bf60e4` (`chore(phase-0): record verified
  preflight`). The bootstrap LICENSE/holder requirement and Phase 0 exit gate remain open.
- 2026-09-19 — Follow-up verification: Git `user.name` and `user.email` were both unset. The user-reported
  Billing-console alarm could not be independently verified: redacted `zsh -lic '... aws budgets describe-budgets
  --account-id "$ACCOUNT" --region us-east-1 ... --output json'` reached the account but returned
  `AccessDeniedException` for `budgets:ViewBudget`; no budget facts were verified, so H5 remains pending.

## Errors & Fixes
- 2026-09-19 — `doctor.sh` exited 1 with missing prerequisites → the machine lacks the Phase 0 toolchain → human
  must install the listed tools; verification is pending a second doctor run.
- 2026-09-19 — `make setup` exited 2 because `/bin/bash: python3.12: command not found` → Python 3.12 is absent →
  install the Phase 0 toolchain, then rerun `make setup`; no environment was created.
- 2026-09-19 — A doctor run from the persisted non-login agent shell falsely reported Homebrew tools missing →
  its PATH predated installation → reran through a fresh zsh login shell; doctor exited 0 with all required tools present.
- 2026-09-19 — `npm install` emitted ERESOLVE peer-dependency warnings while resolving React 19 with
  `@xstate/react`, but did not fail → keep the lockfile install as-is; no legacy-peer-deps override was warranted.
- 2026-09-19 — `aws bedrock-runtime converse --model-id us.anthropic.claude-opus-5` returned
  `AccessDeniedException: anthropic.claude-opus-5 is not available for this account` → the account lacks access
  to the selected Claude profile (Anthropic access form/H4 is the documented cause) → omitted the Claude alias;
  AWS identity plus both Nova converse smoke calls verified the remaining Bedrock path.
- 2026-09-19 — `make web-bootstrap` returned `AccessDeniedException` for `amplify:ListApps` → the current IAM
  identity has no Amplify read permission → no IAM change was authorized; use the AWS console fallback and verify
  the resulting `.pact/amplify.json`/URL before continuing.
- 2026-09-19 — Read-only `aws budgets describe-budgets` exited 254 with
  `AccessDeniedException` because the current IAM principal lacks `budgets:ViewBudget` → the budget alarm could
  not be verified → retain H5 pending and require a permitted read-only check or console-visible facts.

## Open Issues
- (none yet)

## Metrics (only real runs; cite source)
| Cohort | Attempts | Passes | Pass rate | 95% CI | Round acc. | Source (command / file / date) |
|---|---|---|---|---|---|---|
