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
- Repo URL: —
- Web URL (Amplify): —
- API URL: —
- Stack: pact-dev (us-east-1) — not deployed
- Bedrock models verified (alias=id): — (fill in during Phase 0 discovery)
- Scaffold: validated reference copied; bootstrap LICENSE/commit pending
- Human pass rate (study cohort): — · Best agent pass rate: —
- Last green commit: —
- Blockers: H1 deadline confirmation pending · Phase 0 toolchain missing · LICENSE holder needed

## Next Steps
- [ ] H1: confirm the submission deadline from the schedule, Discord, or email
- [ ] Phase 0: install missing toolchain items, then re-run doctor
- [ ] Phase 0: provide the LICENSE copyright holder, then finish task 0.3
- [ ] Phase 0: once H1 is answered, record task 0.1 and continue with task 0.2

## Human-Blocked
- 2026-09-19 — H1: confirm the submission deadline. Open https://www.wemakedevs.org/aws/first-commit/schedule
  (or check Discord/email), then tell Claude Code the exact deadline and timezone. No compression decision can be
  made until this is confirmed.
- 2026-09-19 — Phase 0 toolchain: on macOS run `brew install python@3.12 node awscli aws-sam-cli` and install/start
  Docker Desktop; then re-run `bash docs/reference/scaffold/scripts/doctor.sh`. AWS credentials cannot be checked
  until the AWS CLI is installed.
- 2026-09-19 — Phase 0 task 0.3: initialized a new Git repository on `main` and copied the validated reference
  scaffold into the workspace. `git config user.name` is empty; tell Claude Code the exact copyright holder string
  so it can create the MIT LICENSE and make the bootstrap commit.
- 2026-09-19 — Phase 0 task 0.4: install the missing Python 3.12 toolchain before retrying `make setup`; the exact
  command failed at `python3.12 -m venv .venv`.

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

## Errors & Fixes
- 2026-09-19 — `doctor.sh` exited 1 with missing prerequisites → the machine lacks the Phase 0 toolchain → human
  must install the listed tools; verification is pending a second doctor run.
- 2026-09-19 — `make setup` exited 2 because `/bin/bash: python3.12: command not found` → Python 3.12 is absent →
  install the Phase 0 toolchain, then rerun `make setup`; no environment was created.

## Open Issues
- (none yet)

## Metrics (only real runs; cite source)
| Cohort | Attempts | Passes | Pass rate | 95% CI | Round acc. | Source (command / file / date) |
|---|---|---|---|---|---|---|
