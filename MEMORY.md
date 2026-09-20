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
- Deadline: Sun 20 Sep 2026 20:00 IST; submit by 19:45 IST
- Current phase: Sprint S4
- Milestones: M1 human-pass-live [ ] · M2 AI-fails-live [ ] · Early submission [ ] · Final submission [ ]
- Repo URL: https://github.com/satvikviriyala/ARHV (public; main)
- Web URL (Amplify): https://main.d1i6xn1rxjcnkk.amplifyapp.com (user-verified metadata for `pact-web`, appId `d1i6xn1rxjcnkk`; live browser testing found the root shell but asset paths serving that shell as `text/html`, and a later fresh navigation returned 401 Basic-auth, so this remains an unverified live-success claim)
- API URL: —
- Stack: pact-dev (us-east-1) — not deployed; `cloudformation:CreateChangeSet` denied for `liv28`
- Bedrock models verified (alias=id): nova-2-lite=us.amazon.nova-2-lite-v1:0; nova-pro=us.amazon.nova-pro-v1:0; both Nova calls pass; Claude remains unverified/omitted and optional, with no Anthropic form submitted
- Scaffold: validated reference copied; Phase 0 toolchain, setup, baseline, and Nova smoke green; MIT LICENSE and bootstrap commit complete
- License: MIT; copyright holder confirmed as `Venkata Satya Satvik Viriyala`; task 0.3 commit `3e18dbf5f4ebffcbaad61cdd7f9daefc6823c700`
- Baseline: backend 65 passed; ruff/format/eslint/tsc clean; frontend build plus 2 tests passed; Cedar 6-row demo, SAM validation, and containerized SAM build passed
- Human pass rate (study cohort): — · Best agent pass rate: —
- Last green commit: 911085b (`feat(eval): record Bedrock red-team evidence`)
- Amplify artifact check: local `frontend/dist` has root `index.html` and `assets/`; a locally verified zip built from `dist` has those entries at its root; the live deployment remains unverified
- Blockers: H0 IAM AdministratorAccess for `liv28`; disable Amplify branch/app access control or password protection for the public demo, upload a root-correct zip, wait for `Succeed`, and recheck JS/CSS content types plus `#root` · H5 user-reported $10 alarm not independently verifiable (`budgets:ViewBudget` denied)

## Next Steps
- [x] Sprint S0 (15:45–16:05): preflight, Makefile `imu-demo`, green tests, and physical-first augmentation commit
- [ ] Sprint S1 (16:05–17:20): backend integration/local gate and containerized build passed; deploy/cloud smoke blocked by H0
- [ ] Sprint S2 (17:20–18:25): frontend physical and motion paths/local gate passed; Amplify deploy and real-phone test blocked by H0
- [ ] Sprint S3 (18:25–18:50): local evidence, attack table, Cedar demo, and report passed; live evidence and human pilot blocked by H0
- [ ] Sprint S4 (18:50–19:45): truthful README/writeup/video draft prepared; recording, upload, and external submission remain human-blocked
- [x] Prior Phase 0 toolchain, baseline, Bedrock preflight, license, and public GitHub remote
- [ ] Prior Phase 0 Amplify public deployment and budget-alarm verification follow-ups

## Human-Blocked
- 2026-09-20 15:56 IST — H0: safe read-only checks show the current `liv28` principal is not AdministratorAccess-capable (`iam:ListAttachedUserPolicies`, `iam:ListGroupsForUser`, `amplify:ListApps`, and `budgets:ViewBudget` are denied). Console (root/admin) → IAM → Users → `liv28` → Add permissions → Attach policies directly → **AdministratorAccess** → Add. Then run `aws sts get-caller-identity`. No IAM change was made by the agent.
- 2026-09-20 — H15: real-phone tilt verification on the public Amplify URL is not executable because `pact-dev` was not deployed; after H0, open the Amplify HTTPS URL on an iPhone Safari/Android Chrome, allow motion access, pass three times, and report the DevPanel metrics/reasons.
- 2026-09-20 — H16: the three-person study pilot is not executable without the public Amplify URL; after H0/H15, send `https://main.d1i6xn1rxjcnkk.amplifyapp.com/phone?cohort=study` and the laptop `/?cohort=study`, then record exact first-try counts.
- 2026-09-20 — H11: record the ≤2:55 demo from `docs/DEMO_VIDEO.md` with the phone screen plus a hand shot, AWS console cuts, local/live evidence honestly labelled, and upload it Public or Unlisted to YouTube.
- 2026-09-20 — H13: by 19:45 IST submit the hackathon form with the public repo, video URL, truthful writeup, and compliance checklist; save the confirmation screenshot.
- 2026-09-19 — [RESOLVED] H1: the user confirmed the exact deadline as “Sunday, September 20, 2026 at 8:00 PM IST.”
  PLAN’s “Deadline ≥ Sun 18:00” rule therefore applies: merge Phases 4 and 5 into 2 hours and target the video
  at T-4h (16:00 IST).
- 2026-09-19 — [RESOLVED 17:20 IST] Phase 0 toolchain: on macOS run `brew install python@3.12 node awscli
  aws-sam-cli` and install/start Docker Desktop; a fresh login-shell doctor run now passes all required checks.
  LocalStack token remains optional because the default local profile uses DynamoDB Local.
- 2026-09-19 — [RESOLVED] Phase 0 task 0.3: initialized a new Git repository on `main` and copied the validated
  reference scaffold into the workspace. `git config user.name` was empty; the user confirmed the exact holder
  `Venkata Satya Satvik Viriyala`, and the MIT LICENSE plus bootstrap commit `3e18dbf5f4ebffcbaad61cdd7f9daefc6823c700`
  were completed.
- 2026-09-19 — [RESOLVED] Phase 0 task 0.4 toolchain blocker: Python 3.12 and the remaining local tools were
  installed; `make setup` was rerun in a fresh login shell and succeeded.
- 2026-09-19 — [OPTIONAL] H4: Claude vision access is not required because both verified Nova models are callable.
  No Anthropic form was submitted; Claude remains unverified and omitted from `AgentModels`.
- 2026-09-19 — Phase 0 task 0.7 Amplify: the current IAM user lacks `amplify:ListApps`. In the AWS Amplify
  console (us-east-1), create `pact-web` with “Deploy without Git”, branch `main`, and the SPA rewrite; record
  `{"appId":"…","branch":"main","url":"https://main.<appId>.amplifyapp.com","region":"us-east-1"}` in
  `.pact/amplify.json`, then tell Claude Code the app id/URL. IAM changes are not requested.
- 2026-09-19 — Amplify 404 follow-up: in the existing app's `main` branch, choose “Deploy updates” and drag a
  zip whose top level is `index.html` plus `assets/`; do not upload a parent `frontend/dist` directory. Wait for
  the deployment job to show `Succeed`, then provide the app id/URL so the live root can be checked.
- 2026-09-19 — [PARTIALLY RESOLVED] Amplify metadata: the user verified app `pact-web` (`d1i6xn1rxjcnkk`),
  branch `main`, region `us-east-1`, and URL `https://main.d1i6xn1rxjcnkk.amplifyapp.com`; those four fields
  are recorded in `.pact/amplify.json`, and `AllowedOrigins` now includes localhost plus that exact URL. The
  manual deployment still returns 404, so the human must upload a root-correct zip (`index.html` and `assets/`
  at the top level), wait for `Succeed`, and confirm the live URL. The valid SPA rewrite is unchanged.
- 2026-09-19 — [SUPERSEDED] H5 originally asked for an email for the documented create command or console creation;
  the user now reports the alarm was already created, so no budget create/update/delete action is authorized.
- 2026-09-19 — [RESOLVED] LICENSE holder: `git config --show-origin --get-regexp '^user\.(name|email)$'` returned no
  entries; the user then confirmed `Venkata Satya Satvik Viriyala`. That exact string was used after
  `Copyright (c) 2026`; it was not inferred from the machine username or auto-generated commit identity.
- 2026-09-19 — H5 verification: the user reports the `$10` monthly gross-usage alarm was created in the Billing
  console, but the read-only AWS CLI check was denied by missing `budgets:ViewBudget`. No budget facts were
  returned; keep H5 pending and user-reported until a permitted read-only check or console-visible facts can be
  supplied without sharing an email address.
- 2026-09-19 — [ACTION REQUIRED] Live browser testing at
  `https://main.d1i6xn1rxjcnkk.amplifyapp.com/` verified that the HTML shell returned 200 (517 bytes), but
  `/assets/index-C4NgNJr.js` and `/assets/index-D6lFZ5CM.css` returned the same HTML shell as `text/html`;
  the browser reported `Failed to fetch dynamically imported module` for the JS asset, so React never ran.
  A later fresh navigation returned 401 Basic-auth, meaning Amplify branch/app access control may be enabled.
  The user must disable branch/app access control or password protection for the public demo, upload a ZIP whose
  root contains `index.html` and `assets/`, wait for the deployment to show `Succeed`, then recheck the JS/CSS
  responses (real asset content types and bodies) and confirm the browser renders `#root`. The local build
  remains separate: `frontend/dist` has the expected root files. The valid SPA rewrite is recorded as unchanged;
  no AWS resource or application-code change was made, and the live deployment is not claimed fixed.

## Decisions
- 2026-09-19 — Project = PACT (agent-resistant human verification). Primary challenge = motion-defined glyph `mdg-v1`: single frames carry no information, so screenshot agents get noise. Rejected: drag-to-moving-target (target path had to be sent to the client, trivially scriptable).
- 2026-09-19 — us-east-1 (Bedrock model breadth; Nova 2 Lite needs a `us.`/`global.` profile); arm64 Lambdas; one DynamoDB table; HTTP API; functions split by trust boundary (public API / authorizer / protected action / account token / worker).
- 2026-09-19 — Cedar evaluated with `cedarpy` inside the Lambda authorizer, so the same policy files run locally (Build It) and deployed (Ship It). Rejected: Amazon Verified Permissions (more setup, a second copy of the policies).
- 2026-09-19 — Accessible path = Cognito-verified account → token (assurance=account) → Cedar daily quota of 2 (non-cognitive, WCAG 2.2 SC 3.3.8).
- 2026-09-19 — Generator randomness = keyed SHAKE-256 (`KeyedRng`). Rejected: Mersenne Twister, whose state can be recovered from the published dots, which would reveal hidden dots and the mask.
- 2026-09-19 — Local data plane default = DynamoDB Local (no account). LocalStack is optional: it needs a free auth token since March 2026.
- 2026-09-20 — imu-v1 physical proof family added, thesis screen-only tests are a losing race and vendor attestation is the endgame
- 2026-09-20 — public name is ARHV because PACT is also Private Access Control Tokens (Cloudflare/Chrome/Firefox/Edge/Shopify, June 2026)
- 2026-09-20 — MacBook hinge and fingerprint presence are roadmap-only because there is no public lid-angle API and M1/M2 Macs lack the sensor.
- 2026-09-20 — Added frontend dependency `qrcode` and `@types/qrcode` for the laptop-to-phone QR fallback required by the physical chooser; npm retained the documented React 19 peer warnings and installed with 0 vulnerabilities.

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
- 2026-09-19 — Phase 0 task 0.3 completed: the user confirmed the exact copyright holder
  `Venkata Satya Satvik Viriyala`; root `LICENSE` contains the MIT text with
  `Copyright (c) 2026 Venkata Satya Satvik Viriyala`. The prescribed scaffold/path check, exact-holder/license
  check, Git worktree check, and `git diff --check` passed. Commit:
  `3e18dbf5f4ebffcbaad61cdd7f9daefc6823c700` (`chore: bootstrap PACT from validated reference scaffold`).
- 2026-09-19 — Pushed the verified Phase 0 commits through `838f334` to public `origin/main`; no phase tag
  was created because the Phase 0 exit gate remains open.
- 2026-09-19 — Fresh Phase 0 verification: `zsh -lic 'bash docs/reference/scaffold/scripts/doctor.sh'` passed all
  required checks; `make test-backend` passed 20 tests; `make lint` passed ruff/format/eslint/tsc; frontend
  build and Vitest passed (2 tests); `make cedar-demo` printed 6 decisions; `cd backend && sam validate --lint`
  passed; Nova 2 Lite and Nova Pro converse smoke calls returned OK; `gh repo view` confirmed public `ARHV` on
  `main`; worktree was clean before this MEMORY update.
- 2026-09-19 — Fresh `zsh -lic 'make web-bootstrap'` failed before app creation with the exact
  `AccessDeniedException` for `amplify:ListApps` on
  `arn:aws:amplify:us-east-1:474668382160:apps/*`; `.pact/amplify.json` is absent and
  `backend/samconfig.toml` still allows only `http://localhost:5173`.
- 2026-09-19 — Amplify 404 diagnosis: read-only `aws amplify list-apps` was denied for the current IAM user;
  no `.pact/amplify.json` or Amplify URL exists. `zsh -lic 'cd frontend && npm run build'` passed;
  `frontend/dist/index.html` exists, and a zip built from `dist` was verified to contain root `index.html` plus
  `assets/` (not `frontend/dist/index.html`). The supplied catch-all rewrite was left unchanged; a nested
  folder in a manual upload remains the likely cause, but the live site was not independently verified.
- 2026-09-19 — Fresh redacted/read-only
  `aws budgets describe-budgets --account-id "$ACCOUNT" --region us-east-1` failed with the exact
  `AccessDeniedException` for `budgets:ViewBudget`; the user-reported `$10` alarm remains not independently
  verifiable and no budget mutation was attempted.
- 2026-09-19 — Committed this Phase 0 reconciliation as `8f6318a`
  (`docs(phase-0): record exact deadline and gate status`); no phase tag was created and Phase 1 was not started
  because the Amplify and budget exit-gate items remain incomplete.
- 2026-09-19 — User supplied verified Amplify metadata for `pact-web`: appId `d1i6xn1rxjcnkk`, branch `main`,
  URL `https://main.d1i6xn1rxjcnkk.amplifyapp.com`, region `us-east-1`. Created `.pact/amplify.json` with
  exactly those four fields (the existing `.pact/` gitignore remains unchanged) and patched only
  `AllowedOrigins` to `http://localhost:5173,https://main.d1i6xn1rxjcnkk.amplifyapp.com`; verified Nova
  `AgentModels` aliases and all other samconfig parameters remain unchanged.
- 2026-09-19 — Configuration checks passed: exact metadata assertion, `git diff --check`, ReadLints with no
  errors, and `zsh -lic 'sam validate --lint'` (`backend/template.yaml is a valid SAM Template`). The
  user's manual frontend deployment still returns 404; no deployment/live-success claim was made, and the
  valid SPA rewrite remains unchanged. Root-correct console upload plus `Succeed`/live-URL confirmation and
  H5 budget verification remain pending.
- 2026-09-19 — Live Amplify diagnosis recorded without changing AWS resources or application code: the local
  build/package is root-correct, but the still-unverified deployment serves the HTML shell for JS/CSS asset
  requests, preventing React startup; the later 401 Basic-auth response leaves public access control as a
  possible second blocker. The valid SPA rewrite remains unchanged.
- 2026-09-20 15:56 IST — Sprint S0 started. `aws sts get-caller-identity` confirmed `liv28`; safe read-only
  IAM, Amplify, and Budgets checks were denied, so H0 remains human-blocked. Snapshot, sprint Next Steps, and
  the physical-first naming/roadmap decisions were updated before code work.
- 2026-09-20 15:59 IST — Sprint S0 gate passed: `make test` reported backend 44 passed and frontend 4 passed;
  `make imu-demo` printed the six-row attack table with five rejected attacks and the physics-consistent simulator
  passed; `git diff --check` and ReadLints were clean. Committed as `d56bf89` (`feat: physical-first ARHV
  augmentation (imu-v1)`); moving to S1 backend integration.
- 2026-09-20 16:05 IST — S1 local backend gate passed: `make test-backend` = 65 passed, `make lint` passed
  ruff/format/eslint/tsc, `cd backend && sam validate --lint` accepted the template, and ReadLints reported no
  errors. Implemented utilities, DynamoDB store, stats, API handlers for mdg-v1/imu-v1, authorizer, booking,
  account exchange, worker stub, and smoke script. Committed as `9f8a6ed` (`feat(api): integrate imu-v1
  verification backend`); deploy and cloud smoke remain.
- 2026-09-20 16:46 IST — `make build` first hit the stopped Docker daemon; after starting Docker Desktop,
  the retry completed with `Build Succeeded` for the arm64 layer and all six functions. `make deploy` rebuilt
  from cache but failed before creating the stack: `AccessDenied` for `cloudformation:CreateChangeSet` on
  `aws-sam-cli-managed-default`. No AWS mutation or retry was attempted; S1 cloud acceptance is blocked by H0,
  and the local/S2 fallback is active.
- 2026-09-20 16:40 IST — S2 local gate passed: `npm run lint`, `npx vitest run` (5 files, 10 tests), and
  `npm run build` passed; final `make test` passed backend 65 and frontend 10, and `make lint` passed. The
  physical-first Home, `/phone`, chooser/QR, motion puzzle, booking card, DevPanel, and placeholder Lab/About/
  Account routes were committed in `4a93944` (`feat(web): ship physical-first verification UI`).
- 2026-09-20 16:40 IST — The stack-dependent `make web-env` could not run because `pact-dev` does not exist after
  the blocked deploy. The local data plane eventually ran in Docker; the canonical host bootstrap collided with
  Cursor's listener on `127.0.0.1:8000`, so the table was bootstrapped through the `pact-local` Docker network.
  The smoke script's `PACT_SMOKE_DDB_ENDPOINT` override then enabled a full local run: all health, mdg, Cedar
  booking/replay, stats, imu pass/booking/replay, and orientation-spoof checks were `OK`.
- 2026-09-20 17:18 IST — S3 evidence completed locally: `API=http://127.0.0.1:3000 make bench BACKEND=bedrock
  MODEL=nova-2-lite K=4 N=10` ran twice with 20 valid attempts total, 0/20 full passes, 12/60 correct rounds,
  0 invalid rounds, and 0 infrastructure-error attempts; `make imu-demo IMU_API=http://127.0.0.1:3000`,
  `make cedar-demo`, and `API=http://127.0.0.1:3000 make report` all completed. Report and raw JSONL are in
  `eval/`; commit `911085b` (`feat(eval): record Bedrock red-team evidence`).
- 2026-09-20 17:25 IST — S4 submission materials prepared: README now reports the real 20-challenge local Nova
  result and does not claim a live deployment; `docs/SUBMISSION.md` includes the Cursor Agent/GPT-5.6 Luna
  disclosure, exact result, and current compliance state; `docs/DEMO_VIDEO.md` uses the observed result and
  requires human counts only after H16. Committed as `ee7a8ad` (`docs: prepare truthful submission draft`).

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
- 2026-09-19 — Fresh `make web-bootstrap` exited 2 with
  `botocore.exceptions.ClientError: An error occurred (AccessDeniedException) when calling the ListApps operation:
  User: arn:aws:iam::474668382160:user/liv28 is not authorized to perform: amplify:ListApps on resource:
  arn:aws:amplify:us-east-1:474668382160:apps/* because no identity-based policy allows the amplify:ListApps action`
  → current IAM still cannot inspect or create the app → use the documented console fallback and record the app
  state before closing Phase 0.
- 2026-09-19 — User-reported Amplify 404 could not be confirmed because no app id, `.pact/amplify.json`, or URL
  was available to query. Local build and root-level packaging passed, so no rewrite or source-code change was
  justified → re-upload the `dist` contents at the deployment root and verify the deployment job in the console.
- 2026-09-19 — Live Amplify navigation loaded the 517-byte HTML shell at 200, but the JS and CSS asset URLs
  returned that shell with `Content-Type: text/html`, producing `Failed to fetch dynamically imported module`
  and preventing React from running → the deployed package/root is wrong or Amplify fallback behavior is
  catching static assets; a later fresh navigation also returned 401 Basic-auth, so branch/app access control
  may be enabled → the user must disable public-demo access control/password protection and upload a ZIP with
  `index.html` and `assets/` at its root, then wait for `Succeed` → verify unauthenticated access, JS/CSS
  content types and bodies, no dynamic-import error, and a rendered `#root`. Keep the valid SPA rewrite
  unchanged; the local `frontend/dist` build is not evidence that the live deployment is fixed.
- 2026-09-19 — Initial `sam validate --lint` exited 127 because the persisted shell could not find `sam` on its
  PATH → reran the same validation through a fresh `zsh -lic` login shell → SAM validation passed; no template
  or configuration error was found.
- 2026-09-20 15:56 IST — Read-only IAM policy/group inspection and Amplify/Budgets checks returned
  `AccessDenied` for `liv28` → the current principal cannot verify or grant AdministratorAccess → no IAM
  mutation was attempted; added H0 and continued with local S0 work. Verification: `aws sts get-caller-identity`
  passed and the denied actions were recorded exactly.
- 2026-09-20 16:00 IST — Initial S1 inspection found the documented backend handler/store files absent from the
  working tree (only the reference core modules were present) → the scaffold had not materialized the Phase 1
  implementation → created the documented utilities, handlers, store, tests, and smoke script. Verification:
  `make test-backend` passed 65 tests and `make lint` passed.
- 2026-09-20 16:03 IST — Moto rejected `verify_handoff` because its update supplied unused `:expires`, then
  rejected `deliver_handoff` because its condition lacked `:verified` → removed the unused value and supplied
  the missing condition value. Verification: targeted handoff test passed and full `make test-backend` passed
  65 tests.
- 2026-09-20 16:04 IST — `make lint` first reported six import-order/unused-import diagnostics → applied Ruff's
  minimal import fixes and formatter. Verification: `make lint` passed with 48 files formatted.
- 2026-09-20 16:43 IST — `make build` exited because SAM's container build could not connect to Docker
  (`docker.sock` absent) → Docker Desktop was not running → started Docker Desktop and retried. Verification:
  `docker info` reported server 29.8.0 and the second `make build` passed.
- 2026-09-20 16:46 IST — `make deploy` failed during SAM managed-resource setup with
  `AccessDenied ... cloudformation:CreateChangeSet` for `liv28` → the IAM principal lacks CloudFormation deploy
  permission → stopped after the definitive authorization diagnosis; no IAM edit, stack deletion, or destructive
  fallback was attempted. The exact H0 AdministratorAccess step remains the required human action.
- 2026-09-20 16:29 IST — Initial S2 frontend gate failed on React hook state-in-effect lint rules and an unused
  API payload assignment → derived token claims with `useMemo`, deferred initial loads through a timer, moved
  failure copy to `lib/reasons.ts`, and removed the assignment. Verification: frontend lint passed.
- 2026-09-20 16:29 IST — Frontend build then reported incompatible motion/physical verification callback detail
  types → widened Home and Phone callbacks to accept either assurance and optional metrics. Verification:
  `npm run build` and the final frontend gate passed.
- 2026-09-20 16:37 IST — First local smoke returned `mdg stats: FAIL`; the local API log showed `AttributeError`
  for missing `stats.CHANCE_ROUND` → added the documented constants plus a regression assertion. Verification:
  rebuilt SAM and the Docker-network local smoke passed every check.
- 2026-09-20 16:01 IST — `make web-env` returned `ValidationError: Stack with id pact-dev does not exist` after
  the CloudFormation deploy denial → no frontend environment was generated and no live URL is claimed.
- 2026-09-20 16:02 IST — `make local-up` exhausted its 30-second bootstrap window and the retry still hit a
  404 because Cursor owns host `127.0.0.1:8000` while Docker publishes DynamoDB there → confirmed the container
  healthy and bootstrapped `pact-local` through a one-shot container on the `pact-local` network; local smoke
  then passed. No AWS resource was touched.
- 2026-09-20 17:20 IST — S3 Ruff gate initially found import ordering and S310 URL-audit diagnostics in
  `redteam/bench.py` and `redteam/report.py` → sorted imports, validated URLs as http/https, and retained
  narrowly scoped S310 annotations only on those validated requests. Verification: `make lint` passed.
- 2026-09-20 17:12 IST — `eval/report.md` initially collapsed all stats cohorts to `public` → stats items omitted
  the cohort attribute → added the attribute to the DynamoDB `SET` expression and regression coverage, reset only
  the in-memory local table, reran the two N=10 Bedrock cohorts, and regenerated the report. Verification:
  `make test-backend` passed 65, `make lint` passed, and `eval/report.md` now records the agent cohort.

## Open Issues
- (none yet)

## Metrics (only real runs; cite source)
| Cohort | Attempts | Passes | Pass rate | 95% CI | Round acc. | Source (command / file / date) |
|---|---|---|---|---|---|---|
| agent:nova-2-lite:k4 | 20 | 0 | 0.0000 | [0.0000, 0.1611] | 0.2000 | `eval/report.md`, local API Bedrock runs, 2026-09-20 |
