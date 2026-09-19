# PHASE 0: Setup & preflight (budget 1 h · Sat 16:00–17:00 IST)

**Goal:** a working repo with the validated scaffold in place, green baseline tests, confirmed AWS + Bedrock access,
the Amplify URL known (for CORS), and the repo pushed. Nothing is deployed yet.
**Read first:** `CLAUDE.md`, `PLAN.md`, `docs/reference/README.md`, `docs/AWS_INFRA.md §1–2, §5, §7`,
`docs/REDTEAM_AGENT.md §2`, `docs/HUMAN_STEPS.md`.

## Tasks
**0.1 Deadline (H1).** Ask the human for the confirmed deadline if MEMORY.md says UNCONFIRMED. Write it into
Snapshot. If it's earlier than Sun 23:59 IST, apply `PLAN.md › Compression` now and log the decision.

**0.2 Toolchain.** Run `bash docs/reference/scaffold/scripts/doctor.sh`. For each MISSING item, tell the human the
exact install command (macOS: `brew install python@3.12 node awscli aws-sam-cli`, Docker Desktop; Linux: distro
packages / official installers). AWS credentials missing → Human-Blocked H2; continue with 0.3–0.5 meanwhile.

**0.3 Git + scaffold.**
```bash
git rev-parse --is-inside-work-tree 2>/dev/null || git init -b main
cp -Rn docs/reference/scaffold/. .          # GNU cp may warn that -n is non-portable: harmless
ls backend/template.yaml backend/layers/core/pact_core/mdg.py frontend/package-lock.json Makefile scripts/doctor.sh
```
Create `LICENSE` (MIT, "Copyright (c) 2026 <holder>"; holder = `git config user.name`, or ask). Commit:
`chore: bootstrap PACT from validated reference scaffold`.

**0.4 Environments.** `make setup` (creates `.venv` with Python 3.12, installs `backend/requirements-dev.txt`, runs
`npm install` in `frontend/`, which respects the lockfile). If `npm install` errors with ERESOLVE, use
`npm install --legacy-peer-deps` and log it (docs/FRONTEND.md).

**0.5 Baseline gate.**
```bash
make test-backend            # expect: 20 passed
make lint                    # ruff + format check + eslint + tsc -b: all clean
cd frontend && npm run build && npx vitest run && cd ..     # build OK, 2 tests pass
make cedar-demo              # prints the 6-row decision table
cd backend && sam validate --lint && cd ..                  # template valid
```
Any failure here means the environment differs from the validated one. Fix it via docs/SELF_CORRECTION.md before continuing.

**0.6 AWS + Bedrock preflight (needs H2).**
```bash
aws sts get-caller-identity
aws bedrock list-inference-profiles --region us-east-1 --query "inferenceProfileSummaries[].inferenceProfileId" \
  --output text | tr '\t' '\n' | grep -Ei 'nova|claude' | sort
aws bedrock-runtime converse --region us-east-1 --model-id us.amazon.nova-2-lite-v1:0 \
  --messages '[{"role":"user","content":[{"text":"Reply with OK"}]}]' --query 'output.message.content[0].text'
aws bedrock-runtime converse --region us-east-1 --model-id us.amazon.nova-pro-v1:0 \
  --messages '[{"role":"user","content":[{"text":"Reply with OK"}]}]' --query 'output.message.content[0].text'
```
Pick the strongest Claude *vision* profile in the list (newest Sonnet/Opus-class `us.anthropic.…`) and try the same
`converse`. AccessDenied → Human-Blocked **H4** (Anthropic use-case form); leave Claude out until approved.
Update `backend/samconfig.toml` `parameter_overrides` to include the verified aliases, keeping the other keys:
`AgentModels=\"nova-2-lite=us.amazon.nova-2-lite-v1:0,nova-pro=us.amazon.nova-pro-v1:0[,claude=<profile>]\"`.
Record the verified alias=id list in MEMORY Snapshot. If Nova Pro isn't callable, drop it (don't guess ids).

**0.7 Amplify app (for CORS).** `make web-bootstrap`. It creates the app `pact-web` + branch `main`, sets the SPA
rewrite, and patches only `AllowedOrigins` in samconfig (other parameters are preserved). Record the URL
(`https://main.<appId>.amplifyapp.com`) in Snapshot. If the script fails, see docs/AWS_INFRA.md §5 and log it.

**0.8 Budget alarm (H5).** Ask the human for an email, then run the command in docs/AWS_INFRA.md §7 (it's an "ask"
permission). Or the human creates it in the Billing console. Record "budget alarm: yes".

**0.9 GitHub (H6).** If `gh auth status` works: `gh repo create pact --public --source . --push` (asks permission).
Otherwise the human creates an empty public repo; then `git remote add origin <url> && git push -u origin main`.
Record the repo URL in Snapshot.

**0.10 Close the phase.** Update MEMORY.md (Snapshot: phase 1 next, models, URLs; Log; Next Steps = Phase 1 tasks).
`git tag phase-0-done && git push --tags`.

## Exit gate (all true)
- [ ] Deadline confirmed (or compression decision logged) · [ ] doctor has no MISSING
- [ ] 20 backend tests pass · lint clean · frontend builds and tests · `sam validate --lint` OK
- [ ] `converse` OK for ≥ 1 Nova model; `AgentModels` set; Claude status known
- [ ] Amplify URL recorded; samconfig `AllowedOrigins` includes it · [ ] budget alarm · [ ] repo pushed (public)

## If things go wrong
Missing tools → human installs (don't hand-roll alternatives). Bedrock blocked → R3. `web-bootstrap` fails → R10
(create the app in the console: "Deploy without Git", note the app id in `.pact/amplify.json` manually as
`{"appId": "...", "branch": "main", "url": "https://main.<appId>.amplifyapp.com", "region": "us-east-1"}`).
