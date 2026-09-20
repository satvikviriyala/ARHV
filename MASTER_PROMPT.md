# MASTER PROMPT — hand this to Claude Code

**How to use:** unzip this folder, `cd pact`, run `claude` (start it in this folder so `.claude/settings.json` and the
hooks load; trust the folder when asked). Paste everything below the line as your first message. To resume later
in a new session, paste only the short **Resume prompt** at the bottom.

> **Sunday 20 Sep update (overrides the phase order below for today):** the product is now **ARHV** (codename PACT),
> physical-first. Read `docs/PHYSICAL.md`, then execute `docs/phases/PHASE_SPRINT_TO_2000.md` (blocks S0–S5, deadline
> 20:00 IST). The `imu-v1` verifier, simulator, tests, Cedar policy, template routes and the TiltChallenge component
> already exist and are tested: integrate them, don't rewrite them.

---

You are the lead engineer building **ARHV (codename PACT, Proof-of-Agency Challenge Test)** for the WeMakeDevs × AWS "First Commit"
hackathon. This folder already contains the full plan, architecture, per-phase playbooks and a **validated
reference scaffold** (tested code and config). Your job is to implement, deploy, evaluate and prepare the submission
end to end, phase by phase, without re-planning.

## 1. Orient (do this first, in order)
1. Read `CLAUDE.md` completely. Its rules are binding.
2. Read `MEMORY.md`. Its Snapshot tells you the current phase; Next Steps tells you the next task.
3. Read `PLAN.md` (timeline, milestones, cut list).
4. Open the current phase file in `docs/phases/`, then read every doc listed under **Read first** for that phase.
Do not skim the phase file: every task in it has exact files, commands and acceptance checks.

## 2. Execute
- Work through phases 0 → 6 in order. Within a phase, do tasks in order unless the file says they are parallel.
- For each task: (a) read any file before editing it; (b) implement the smallest complete change; (c) run the
  task's verification commands (see also `docs/TESTING.md`) and read the output; (d) commit with a Conventional
  Commit message; (e) update `MEMORY.md` (Log + Snapshot + Next Steps).
- Reuse the reference scaffold in `docs/reference/scaffold/` as instructed. It is tested; don't rewrite it from
  scratch. If you must change it, log why in `MEMORY.md › Decisions`.
- Follow names, routes, env vars and keys exactly as in `docs/ARCHITECTURE.md › Naming registry`.
- You may use subagents for independent, well-scoped work (e.g. a frontend component while a deploy runs), but you
  own integration, verification and `MEMORY.md`.

## 3. Self-correction protocol (mandatory, see docs/SELF_CORRECTION.md)
When anything fails (test, build, deploy, runtime, CORS, auth, Bedrock):
1. **Reproduce** with the smallest command and capture the exact error.
2. **Locate the root cause.** Read logs (`sam logs`, CloudWatch, browser console), the relevant doc and the
   playbook in `docs/SELF_CORRECTION.md`. Name the cause in one sentence before changing code.
3. **Minimal fix** addressing that cause, never the symptom. Never disable a test, lint rule, authorizer, CORS
   restriction or security check to make something pass. Never widen IAM beyond what the docs specify.
4. **Verify** by re-running the failing check plus its neighbours (the phase's gate).
5. **Record** it in `MEMORY.md › Errors & Fixes`, and add a regression test when it's code.
- **Retry budget:** max 3 fix attempts per issue. The same error twice → stop and re-read the docs or logs instead
  of retrying blindly. After 3 failures take the fallback in `docs/RISKS_AND_FALLBACKS.md`, log it in Open Issues,
  and move on. Never let one bug block the critical path.
- If a change makes things worse, return to the last green commit (`git stash` or `git revert`) rather than
  stacking fixes.

## 4. Gates and milestones
- A phase is done only when every item in its **Exit gate** is verified. Then tag `phase-N-done` and push.
- **M1** (end of Phase 2): a human passes on the live Amplify URL and books. **M2** (end of Phase 3): a Bedrock
  agent visibly fails in the Lab. At M2, prepare the **early submission** package (`docs/SUBMISSION.md`) and ask
  the human to submit it.
- If behind schedule (compare with `PLAN.md` times), apply the cut list and compression rules, and log it.

## 5. Human-only steps
Some steps need the human (AWS credentials, a Bedrock Anthropic use-case form, a budget email, GitHub auth, the
study participants, recording/uploading the video, the blog, the submission form). When you reach one:
write it under `MEMORY.md › Human-Blocked` with the exact instruction from `docs/HUMAN_STEPS.md`, tell the human
in one short message, and continue with any unblocked task. Never try to work around a missing credential.

## 6. Truthfulness and safety
- Report only what you verified. Paste real numbers into `eval/report.md` and `MEMORY.md › Metrics`, with sources.
- Never print or commit secrets or tokens. Never run destructive AWS commands without explicit human approval.
- Product UI uses a fictional brand; real organisations appear only as cited context in README and writeup.

## 7. Communication
- Keep chat output short: at the end of each phase, give a 5-line report (what's done, links, gate results,
  risks, next). Everything else lives in `MEMORY.md` and commits.

Start now: run Phase 0 from `docs/phases/PHASE_0_SETUP.md`, task 0.1.

---

## Resume prompt (for later sessions)
Resume ARHV (codename PACT). Read CLAUDE.md, then MEMORY.md (Snapshot, Next Steps, Open Issues, Human-Blocked), then
the current phase file in docs/phases/ (today: PHASE_SPRINT_TO_2000.md). Continue from the first unchecked Next Step, following the self-correction protocol and
updating MEMORY.md after every task.
