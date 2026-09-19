# PHASE 3: Red team → M2 + early submission (budget 4 h · Sun 08:00–12:00 IST)

**Goal (M2):** from the Lab page, a Strands agent on Amazon Bedrock attacks a fresh puzzle; the page shows "What the
AI saw" (noise frames) next to "What you see" (animated), the AI's wrong answers and the verdict; the scoreboard
compares humans and agents. Then submit an early version (the form stays editable).
**Read first:** `docs/REDTEAM_AGENT.md` (all), `docs/API.md` (agent-runs), `docs/DATA_MODEL.md` (RUN, LIMIT),
`docs/FRONTEND.md §6`, `docs/EVALUATION.md §5, §7`, `docs/SUBMISSION.md §2`.

## Tasks
**3.1 Worker.** Implement `functions/agent_worker/app.py` per docs/REDTEAM_AGENT.md §4 using the scaffold's
`pact_agent`. `test_worker.py`: monkeypatch `pact_agent.models.build_model` to return the fake model from
`test_agent.py`; moto S3 + DynamoDB; assert queued → running → done, 3 rounds × K PNGs in S3, stats cohort
`agent:<alias>:k<K>`, `challengeId` stored; model error → `error` status and **no** stats.

**3.2 API.** `start_agent_run`, `get_agent_run` (+ `?replay=1` only when done) in `functions/api/app.py`. Tests:
unknown alias 400; frames ∉ {1,4,8} 400; cap reached 429 (set cap 1); `LOCAL_DEV` 501; `lambda.invoke` called with
`InvocationType="Event"` (monkeypatch the client); presigned URLs present; replay absent until done.

**3.3 Deploy + smoke.** `make deploy` → `make smoke` (now **with** step 10). Check `sam logs -n AgentWorkerFunction`
for `agent_round` lines.

**3.4 Lab page.** Controls, `startAgentRun` + polling, `AgentRunView` side by side (AI frames `<img>` vs live
`MdgCanvas` from `replay`), verdict banner, full `Scoreboard`. Loading/error states (daily cap → friendly message).

**3.5 Bench CLI + pilot.** Implement `redteam/bench.py` (+ `redteam/__init__.py`) per §5. Run
`make bench BACKEND=bedrock MODEL=nova-2-lite K=4 N=10` against the cloud API → JSONL in `eval/results/`. Check the
summary: round accuracy near 1/6? If the lower CI bound > 0.25, follow docs/EVALUATION.md §7 before continuing.

**3.6 Web deploy + M2.** `make web-deploy`. In the browser: run nova-2-lite K=4 → FAILED shown with frames. Tick M2.

**3.7 Early submission package.** Interim README (pitch, live URL, figure, "work in progress" note, AI tools),
draft writeup (docs/SUBMISSION.md §2, numbers labelled *preliminary*, from the pilot JSONL and `/v1/stats`).
Ask the human to record a rough 60–90 s screen capture of M1 + M2 (H11), upload it to YouTube (Unlisted), and
submit the form (H13). Record "early submission ✓" in Snapshot.

**3.8 Close.** Tests + lint green · MEMORY · `git tag phase-3-done` · push.

## Exit gate
- [ ] **M2** on the live URL: Bedrock run completes, AI frames + live canvas side by side, verdict, scoreboard updates
- [ ] `make smoke` (with agent step) green · worker + API tests green
- [ ] Pilot JSONL committed in `eval/results/` · early submission done (or Human-Blocked with a time)

## If things go wrong
Bedrock errors → R3 and the Bedrock rows of docs/SELF_CORRECTION.md. Worker timeouts → lower K / raise timeout.
If the Lab isn't ready by 11:30, record the early video with the bench CLI output instead. The deadline matters more.
