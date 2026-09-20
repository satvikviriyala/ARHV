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
- Web URL (Amplify): https://main.d1i6xn1rxjcnkk.amplifyapp.com (`pact-web`, appId `d1i6xn1rxjcnkk`; deployment job 9 reported `SUCCEED`; confirmation route, failure state, and retry focus verified in the browser)
- API URL: https://28y0g9h8ki.execute-api.us-east-1.amazonaws.com
- Stack: pact-dev (us-east-1) — `CREATE_COMPLETE`; deployed by `make deploy` on 2026-09-20
- Bedrock models verified (alias=id): nova-2-lite=us.amazon.nova-2-lite-v1:0; nova-pro=us.amazon.nova-pro-v1:0; both Nova calls pass; Claude remains unverified/omitted and optional, with no Anthropic form submitted
- Scaffold: validated reference copied; Phase 0 toolchain, setup, baseline, and Nova smoke green; MIT LICENSE and bootstrap commit complete
- License: MIT; copyright holder confirmed as `Venkata Satya Satvik Viriyala`; task 0.3 commit `3e18dbf5f4ebffcbaad61cdd7f9daefc6823c700`
- Latest gate: backend 70 passed; frontend 14 passed; Ruff/format/ESLint/TypeScript clean; Cedar 7-row demo, SAM validation, and containerized SAM build passed
- Human pass rate (study cohort): — · Best agent pass rate: —
- Last green commit: ff132ee (`feat(web): add booking confirmation flow`)
- Amplify artifact check: local `frontend/dist` has root `index.html` and `assets/`; live root returned 200 `text/html` (792 bytes), JS returned 200 `text/javascript` (415205 bytes), CSS returned 200 `text/css` (23976 bytes); `/booking/confirmed` returned the SPA shell and the browser rendered the ARHV document with no dynamic-import error
- Frontend environment: production/development files generated from `pact-dev` outputs by `make web-env`
- Cloud smoke: `make smoke` passed every listed check, including live `imu-v1` pass/booking/replay/explain and orientation spoof rejection
- Live evidence: `make imu-demo IMU_API=https://28y0g9h8ki.execute-api.us-east-1.amazonaws.com` rejected all five cheap spoofs and passed only the physics-consistent simulator; `make cedar-demo` showed physical ALLOW, replay/quota DENY
- IMU tuning: `tiltErrDeg` budget is now 18° (was 12°) for modest browser sensor-fusion/calibration skew; no gravity, gyro, continuity, target, binding, or token rules changed; focused IMU tests 22 passed
- Frontend refresh: `ARHV Rail` fictional route/date/class/quota flow defaults Bengaluru → Visakhapatnam, lists three fictional services, and contextualises verification as a quick presence check; booking success now navigates to `/booking/confirmed`, while verification/authz failures expose a focused retry; local lint, TypeScript, 14 Vitest tests, and production build passed
- Local evidence: containerized SAM build passed; networked local smoke passed health, both proof families, bookings, replay, stats, spoof, and agent-route checks; local IMU table and Cedar demo passed
- Live evidence: post-deploy `make smoke SMOKE_ARGS=--no-agent` passed all health, mdg, booking/replay, stats, imu, and orientation-spoof checks; live assets returned 200 with `text/javascript`/`text/css`; browser verified Home, contextual chooser focus, the 1/3 motion-puzzle failure copy, and retry focus returning to the first verification option
- Blockers: complete real-phone tilt, human motion-puzzle/study, video, and submission checks · H5 user-reported $10 alarm not independently verifiable (`budgets:ViewBudget` denied)

## Next Steps
- [x] Sprint S0 (15:45–16:05): preflight, Makefile `imu-demo`, green tests, and physical-first augmentation commit
- [x] Sprint S1 (16:05–17:20): backend integration/local gate and containerized build passed; `make deploy` completed with `pact-dev` `CREATE_COMPLETE` and live API output
- [x] Sprint S2 (17:20–18:25): frontend local gate passed and Amplify deployment job 9 succeeded with rail-counter refresh and booking-result UX; real-phone check pending
- [ ] Sprint S3 (18:25–18:50): local/live API evidence, attack table, Cedar demo, and Amplify render passed; human pilot remains
- [ ] Sprint S4 (18:50–19:45): truthful README/writeup/video draft prepared; recording, upload, and external submission remain human-blocked
- [x] Booking-result UX: confirmation route/card, authorization failure state, fresh-challenge retry, focus management, and focused frontend tests
- [x] Prior Phase 0 toolchain, baseline, Bedrock preflight, license, and public GitHub remote
- [x] Prior Phase 0 Amplify public deployment; budget-alarm verification remains pending

## Human-Blocked
- 2026-09-20 15:56 IST — [RESOLVED 17:13 IST] H0: the user granted AdministratorAccess to `liv28`; `make deploy` now completed successfully. No IAM change was made by the agent.
- 2026-09-20 — H15: open the deployed Amplify HTTPS URL on an iPhone Safari/Android Chrome, allow motion access, pass three times, and report the DevPanel metrics/reasons; no real-phone success is recorded yet.
- 2026-09-20 — H16: run the three-person study pilot at `https://main.d1i6xn1rxjcnkk.amplifyapp.com/phone?cohort=study` and `/?cohort=study`, then record exact first-try counts; no human-study result is recorded yet.
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
- 2026-09-20 — Set the `imu-v1` tilt-vs-gravity median-error budget from 12° to 18° per `docs/PHYSICAL.md §3`: the client merges independently timed orientation and motion events, so a modest fusion/calibration offset can reject a coherent human-like trace; gravity, gyro, continuity, targets, binding, and replay semantics remain unchanged. Rejected loosening target/rate checks.
- 2026-09-20 — Reframed the demo counter as a fictional `ARHV Rail` journey search with existing design tokens and no new dependency; route controls stay local to the demo while the protected API booking contract remains unchanged.
- 2026-09-20 — Booking results now use ephemeral React Router state to enter `/booking/confirmed`; existing booking fields provide the fictional reference/seat and local journey state provides route/date/class. Existing `passed:false` verification responses and 401/403 authorization responses keep their contracts and render a fresh-check retry; no backend change or dependency was added.

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
- 2026-09-20 17:30 IST — Final repository gate passed: `make test` = backend 65 passed and frontend 10 passed;
  `make lint` passed Ruff/format/ESLint/TypeScript; `cd backend && sam validate --lint` accepted the template.
  Worktree is clean on `main`, ahead of `origin/main` by 12 commits; live deployment, video upload, and form
  submission remain unverified human actions.
- 2026-09-20 17:03 IST — Pushed the verified physical-first ARHV sprint commits through `193ae70` to public
  `origin/main`; the local implementation is now published. Cloud deployment remains blocked by H0
  (`cloudformation:CreateChangeSet` denied).
- 2026-09-20 17:13 IST — `make deploy` passed after the user granted AdministratorAccess to `liv28`: SAM
  validation and cached arm64 container build passed; CloudFormation created `pact-dev` in `us-east-1` with
  `ApiUrl=https://28y0g9h8ki.execute-api.us-east-1.amazonaws.com`, `TableName=pact-dev`,
  `UserPoolId=us-east-1_LDW5pKgWH`, `UserPoolClientId=3vi5h9e3ch5rnhasascpp0nfbj`, and
  `ArtifactsBucketName=pact-dev-artifactsbucket-mrg5ofgqklqg`. The Make target also wrote the frontend
  environment files. No destructive operation was run.
- 2026-09-20 17:13 IST — `make web-env` passed and regenerated
  `frontend/.env.production.local` plus `frontend/.env.development.local` from the deployed stack outputs.
  It recorded only public API/region/Cognito configuration; no secret was printed or committed.
- 2026-09-20 17:14 IST — `make web-deploy` passed: Vite TypeScript build produced root `dist/index.html`
  plus `assets/`, Amplify app `pact-web` created deployment job 4, job 4 reported `SUCCEED`, and the script
  reported `https://main.d1i6xn1rxjcnkk.amplifyapp.com`. Live unauthenticated asset content types and browser
  rendering are intentionally not claimed until the next verification step.
- 2026-09-20 17:15 IST — `make smoke` passed against
  `https://28y0g9h8ki.execute-api.us-east-1.amazonaws.com`: health, mdg create/wrong/pass, missing and garbage
  token denials, mdg booking/replay/explain, mdg stats, imu pass/booking/replay/explain, orientation spoof
  rejection, and the agent route all printed `OK`; exit code 0. No real-phone result is inferred from this smoke.
- 2026-09-20 17:15 IST — Live `make imu-demo IMU_API=https://28y0g9h8ki.execute-api.us-east-1.amazonaws.com`
  printed `REJECTED` for orientation-only, dead-gyro, desk-flat gravity, teleporting, and replayed-recording
  attacks, and `PASSED` for the physics-consistent simulator. `make cedar-demo` printed physical
  `permit-physical-book` ALLOW, replay `forbid-token-replay` DENY, and account quota 2 DENY.
- 2026-09-20 17:18 IST — Safe live checks initially returned 401 for the Amplify root and both current assets.
  The documented `aws amplify update-app ... --no-enable-basic-auth` and `update-branch ... --no-enable-basic-auth`
  commands completed successfully and reported app/branch basic auth disabled; no IAM or app deletion was used.
- 2026-09-20 17:19 IST — After basic-auth removal, the root returned 200 but both assets returned 200
  `text/html` (793 bytes), identifying the existing catch-all SPA rule as a separate issue. `make web-bootstrap`
  applied the documented asset-safe rewrite, then `make web-deploy` created job 5 (`SUCCEED`). Final checks
  returned root 200 `text/html`, JS 200 `text/javascript`, CSS 200 `text/css`; the browser rendered
  `ARHV · Agent-Resistant Human Verification` with the physical-first home content.
- 2026-09-20 17:19 IST — Browser CDP verified `#root` exists with one child, title
  `ARHV · Agent-Resistant Human Verification`, physical-first ARHV text in the root, and no
  `Failed to fetch dynamically imported module` text.
- 2026-09-20 17:20 IST — Committed the verified deployment record as `86a0c96`
  (`chore(deploy): record live ARHV verification`) and pushed it successfully to public `origin/main`
  (`6e662e7..86a0c96`). No generated environment file or credential was tracked.
- 2026-09-20 17:40 IST — IMU tuning verification passed: `backend/tests/test_imu.py` reported 22 passed; the
  14° fusion-bias regression passed with `tiltErrDeg=14.0`, `targetsReached=3`, and `gyroCorr=[0.992, 0.984]`;
  orientation-only, dead-gyro, and mismatched-gravity spoofs remained rejected. Ruff and ReadLints reported no
  errors. The initial diagnostic omitted `PYTHONPATH` and failed to import `pact_core`; rerunning with
  `PYTHONPATH=backend/layers/core` passed.
- 2026-09-20 17:45 IST — `frontend` gates passed after the rail refresh: `npm run lint`, `npx tsc -b`,
  `npx vitest run` (5 files, 10 tests), and `npm run build`; ReadLints reported no errors. Browser review on
  `http://localhost:5173` verified default route controls, three service cards, contextual `QUICK PRESENCE CHECK`,
  phone QR generation, and `/phone` copy including `Tilt your phone gently`. No real phone or live booking is inferred.
- 2026-09-20 17:48 IST — Full verification passed: `make test` reported backend 66 passed and frontend 10 passed;
  `make lint`, `cd backend && sam validate --lint`, `make build`, `make cedar-demo`, and local
  `make imu-demo IMU_API=http://127.0.0.1:3000` passed. The local smoke suite passed all listed checks from a
  one-shot container on the `pact-local` network because the host port 8000 is occupied by another listener.
- 2026-09-20 17:52 IST — Fresh-login `make deploy` passed: SAM created the new `PactCoreLayer` version and
  updated `pact-dev` to `UPDATE_COMPLETE`; API URL remained `https://28y0g9h8ki.execute-api.us-east-1.amazonaws.com`.
  `make web-env` passed without printing secrets.
- 2026-09-20 17:54 IST — Fresh-login `make web-deploy` passed: Vite built the refreshed frontend, Amplify deployment
  job 6 reported `SUCCEED`, and the live URL remained `https://main.d1i6xn1rxjcnkk.amplifyapp.com`.
  Post-deploy smoke with `--no-agent`, live `imu-demo`, root/asset checks, and browser snapshots of Home and `/phone`
  all passed. No real-phone success is inferred.
- 2026-09-20 17:57 IST — Pushed verified `main` through `fbab01b` to public GitHub `origin/main`; the only
  untracked file is the user-supplied reference screenshot `IRCTC.png`, which was not added or used by the product.
- 2026-09-20 18:27 IST — Implemented the rail result state machine: `BookingCard` routes successful responses to `/booking/confirmed`, 401/403 responses render the exact suspicious-activity retry state, and `Home`/`Phone` preserve journey values while remounting a fresh verification challenge. Added focused success/failure/retry tests and documented the route in `docs/FRONTEND.md`. Commit `ff132ee` (`feat(web): add booking confirmation flow`).
- 2026-09-20 18:27 IST — Final local verification passed: `make test` = backend 70 and frontend 14; `make lint`; `npm run build`; `cd backend && sam validate --lint`; `git diff --check`; and ReadLints all passed.
- 2026-09-20 18:49 IST — `make web-env` refreshed public frontend configuration from `pact-dev`; `make web-deploy` built the bundle and Amplify deployment job 7 reported `SUCCEED`. Live root/assets and `/booking/confirmed` returned 200 with expected HTML/JavaScript/CSS content types.
- 2026-09-20 18:49 IST — `make smoke SMOKE_ARGS=--no-agent` passed every live health, mdg, booking/replay, stats, imu, and orientation-spoof check. No real-phone or human outcome was inferred.
- 2026-09-20 18:51 IST — Canonical `make local-smoke` hit the known host DynamoDB 404; a direct container-IP endpoint did not respond, so it was stopped. The documented Docker-network fallback then passed every local health, mdg, Cedar booking/replay, stats, imu, spoof, and agent-local-fallback check.
- 2026-09-20 18:55 IST — Browser verification after the focus fix produced Amplify deployment job 9 (`SUCCEED`): Home and the chooser rendered, deliberately choosing the first motion option three times produced the live `1/3` failure state with exact copy, and `Try verification again` returned focus to the first verification option. This was a browser failure-path check, not a human or phone pass.

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
- 2026-09-20 17:13 IST — The former CloudFormation authorization failure was resolved by the user's
  AdministratorAccess grant to `liv28`; a fresh `make deploy` verified the minimal recovery with a successful
  `CREATE_COMPLETE` stack and the outputs recorded in Snapshot/Log.
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
- 2026-09-20 17:16 IST — The first scripted live HTTP check exited with `zsh: eval:1: unmatched "` because
  nested shell/Python quoting was malformed → replaced it with a simple `curl` loop → the corrected check
  reproduced the live 401 response, and subsequent documented fixes plus final checks passed.
- 2026-09-20 17:18 IST — Live Amplify root/assets returned 401 → app and branch basic-auth protection was enabled
  → ran the documented non-destructive `--no-enable-basic-auth` updates → corrected check returned root/assets
  200, but assets were still HTML. Verification then isolated the SPA-rule issue and the later rewrite/deploy
  fix produced correct JavaScript/CSS content types and browser rendering.
- 2026-09-20 17:19 IST — Amplify asset requests returned 200 `text/html` → existing `/ <*>` catch-all rewrite
  intercepted static files → ran documented `make web-bootstrap` followed by `make web-deploy` → job 5
  succeeded, JS/CSS content types and byte sizes were correct, and browser snapshot showed the ARHV app.
- 2026-09-20 — Direct IMU margin diagnostic returned `ModuleNotFoundError: No module named 'pact_core'` because
  the standalone command did not include the layer path → reran with `PYTHONPATH=backend/layers/core`; the
  relaxed-trace and spoof outcomes then matched the regression test.
- 2026-09-20 — Local browser `/phone` initially showed `Network error.` at `http://127.0.0.1:5173` because the
  deployed CORS allow-list contains `http://localhost:5173`, not the loopback alias → reopened at
  `http://localhost:5173/phone`; the challenge loaded and the phone UI snapshot passed. No CORS policy was widened.
- 2026-09-20 — Canonical `make local-smoke` reached the API but its host-side DynamoDB read returned HTTP 404
  because the local SAM containers use `dynamodb-local:8000` on the `pact-local` Docker network while host port
  8000 is occupied by another listener → confirmed `pact-local` already existed, then ran the documented
  networked fallback with `PACT_SMOKE_DDB_ENDPOINT=http://dynamodb-local:8000`, dummy local credentials, and
  `host.docker.internal:3000`; all smoke checks passed. An intermediate container command lacked credentials
  (`NoCredentialsError`) and was corrected without changing application code.
- 2026-09-20 — First live asset-check loop used zsh’s special `path` variable and therefore shadowed `PATH`,
  producing `command not found: curl` → renamed the loop variable to `asset`; root and both deployed assets then
  returned 200 with expected content types and sizes.
- 2026-09-20 18:16 IST — `npx vitest run` initially failed two booking-flow assertions because test DOM cleanup was missing and the existing success label is a paragraph, not a heading → added cleanup and corrected the focused assertion → all 14 frontend tests passed.
- 2026-09-20 18:16 IST — `npm run lint` flagged `BookingCard` state resets called synchronously in an effect → removed those redundant resets → frontend lint, typecheck, and build passed.
- 2026-09-20 18:25 IST — Live browser review found `VerifyChooser`’s focus ref attached to the wrong branch/button, so the laptop modal did not focus its first motion option → attached the ref to the actual first option, reran frontend gates, and redeployed → job 9 succeeded and browser snapshots showed the first option focused both on open and after retry.
- 2026-09-20 18:51 IST — `make local-smoke` failed with DynamoDB `GetItem` HTTP 404 because host port 8000 was not the Docker-network DynamoDB endpoint; a host container-IP retry stalled → used the documented one-shot `pact-local` Docker network with `dynamodb-local:8000`, `host.docker.internal:3000`, and dummy local credentials → all local smoke checks passed.

## Open Issues
- (none yet)

## Metrics (only real runs; cite source)
| Cohort | Attempts | Passes | Pass rate | 95% CI | Round acc. | Source (command / file / date) |
|---|---|---|---|---|---|---|
| agent:nova-2-lite:k4 | 20 | 0 | 0.0000 | [0.0000, 0.1611] | 0.2000 | `eval/report.md`, local API Bedrock runs, 2026-09-20 |
