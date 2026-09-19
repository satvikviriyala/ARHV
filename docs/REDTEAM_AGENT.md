# RED TEAM — Strands Agents attacking PACT (Bedrock in the cloud, Ollama locally)

Reference (tested with a fake Strands model): `functions/agent_worker/pact_agent/{models,prompts,solver}.py`,
`backend/tests/test_agent.py`. Verified against `strands-agents 1.56.0`.

## 1. Fairness rules (the result is only meaningful if the attack is strong and honest)
1. **Same puzzle, same verifier.** Agents get challenges from the same generator and are scored by the same
   `mdg.check_answers`; agent attempts go into cohort `agent:<alias>:k<K>`.
2. **Kerckhoffs:** the prompt explains exactly how the puzzle works (motion-defined shape, noise fraction, frame
   spacing). Security must not rely on the attacker not knowing the mechanism.
3. **More than a real browser agent gets:** K **consecutive** frames 33 ms apart, rendered losslessly at 3× scale
   (a real agent's screenshots are slower and irregular).
4. **Strongest available models:** Nova 2 Lite (cheap baseline), Nova Pro, and the strongest Claude vision
   model enabled on the account (Phase 0 discovery). Temperature 0.
5. **One self-repair** if the reply isn't valid JSON with a listed option. Still invalid → scored wrong (reported
   separately as `invalid`).
6. **Infra errors are not agent failures.** If a round has `error` (throttling, AccessDenied), the run is `error`
   and is **not** counted in stats.
7. Report per-round accuracy vs **chance (1/6)** and pass rate vs **chance (1/216)**, with Wilson 95% CIs and N.

## 2. Models
Default aliases (template parameter `AgentModels`, env `AGENT_MODELS`):
`nova-2-lite=us.amazon.nova-2-lite-v1:0,nova-pro=us.amazon.nova-pro-v1:0`. Add `claude=<profile id>` in Phase 0 if
available. Discover what the account can call:
```bash
aws bedrock list-inference-profiles --region us-east-1 \
  --query "inferenceProfileSummaries[].inferenceProfileId" --output text | tr '\t' '\n' | grep -Ei 'nova|claude' | sort
aws bedrock-runtime converse --region us-east-1 --model-id us.amazon.nova-2-lite-v1:0 \
  --messages '[{"role":"user","content":[{"text":"Reply with OK"}]}]' --query 'output.message.content[0].text'
```
- Nova 2 Lite has no in-region endpoint: use the `us.` or `global.` inference profile id, never the bare model id.
- Anthropic models need the one-time use-case form (human step H4). Until then, Claude calls fail with
  `AccessDeniedException`/`ValidationException`, so leave `claude` out of `AgentModels` instead.
- Local (Ollama) vision models, first that `ollama show <model>` lists with the **vision** capability:
  `qwen2.5vl:7b` (≥ 16 GB RAM), `llama3.2-vision:11b`, `gemma3:4b` (8 GB machines). Put the choice in MEMORY.md › Decisions.

## 3. Agent design (`pact_agent`)
- `models.build_model("bedrock", alias)` → `BedrockModel(model_id=…, region_name=BEDROCK_REGION, temperature=0.0,
  max_tokens=400, streaming=False)`. `build_model("ollama", name)` → `OllamaModel(host, model_id=name, temperature=0.0,
  max_tokens=400)`.
- `prompts.build_round_content(pngs, options)` → Converse content blocks: instructions text, then per frame a label
  text block + `{"image": {"format": "png", "source": {"bytes": png}}}` (raw bytes; Strands/Bedrock encode).
- `solver.solve_round(model, pngs, options)` → **fresh `Agent` per round** (`callback_handler=None`, no tools), parse the
  first JSON object whose `answer` is an option (case-insensitive), one repair turn, returns `RoundAttempt`
  (`answer, confidence, rationale, raw, valid, latency_ms, repaired, error`).
- Prompt text is in `prompts.py`; don't weaken it. If you improve it, log the change and re-run the matrix.

## 4. Cloud worker (`functions/agent_worker/app.py`), Phase 3
```
handler({"runId"}):
  run = store.get_run(runId); if not run or run.status != "queued": return
  store.update_run(runId, status="running", startedAt=now, progress=0)
  model = models.build_model("bedrock", run.model)
  seed = token_bytes(32); ch = mdg.generate_challenge(seed); cid = new_id("ch")
  store.put_challenge(cid, seed_hex, answers=ch.answers, cohort=f"agent:{alias}:k{K}", family, now, expires_at=now+600)
  store.update_run(runId, challengeId=cid)      # enables ?replay=1 (Lab "What you see") after the run is done
  for i, rnd in enumerate(ch.public.rounds):
      frames = mdg.decode_frames(rnd.frames)[:K]                 # K consecutive frames
      pngs = [png.render_frame_png(f, scale=3) for f in frames]
      keys = upload each to s3://ARTIFACTS_BUCKET/runs/<runId>/r<i>_f<j>.png (ContentType image/png)
      att = solver.solve_round(model, pngs, rnd.options)
      rounds.append({index:i, options, frameKeys:keys, answer, confidence, rationale, valid, latencyMs, repaired, error})
      store.update_run(runId, rounds=rounds, progress=i+1); log agent_round
  if any(r.error for r in rounds): store.update_run(runId, status="error", error="model_error: …"); return   # not counted
  rec = store.consume_challenge(cid, now)
  passed, correct = mdg.check_answers(rec.answers, [r.answer or "" for r in rounds])
  add truth/correct to each round; store.record_attempt(cohort=…, passed, correct, 3, duration_ms=sum(latency))
  store.update_run(runId, status="done", passed, roundsCorrect=correct, rounds, finishedAt=now); log agent_run_done
  except Exception: store.update_run(runId, status="error", error=type(e).__name__); log.exception
```
IAM: `bedrock:InvokeModel` + `bedrock:InvokeModelWithResponseStream` on `*` (inference profiles route across
regions), S3 CRUD on the bucket, DynamoDB CRUD. Timeout 180 s, 1 GB. Never set reserved concurrency.

## 5. Bench CLI (`redteam/bench.py`), local or cloud, Bedrock or Ollama
```
python -m redteam.bench --api <URL> --backend bedrock|ollama --model <alias or ollama name> --frames 4 --n 20 \
       [--region us-east-1] [--ollama-host http://localhost:11434] [--out eval/results] [--sleep 0.5]
```
Per attempt: `POST /v1/challenges` with header `x-pact-cohort: agent:<label>:k<K>` (label = alias, or
`ollama-<name>` with `:` → `-`), decode frames, render K PNGs with `pact_core.png`, `solve_round` per round, `POST
answers` → `passed`, `roundsCorrect`. Append one JSON line per attempt to
`eval/results/<UTC timestamp>_<label>_k<K>.jsonl`:
```json
{"ts":"2026-09-20T09:12:01Z","api":"https://…","backend":"bedrock","model":"nova-2-lite","modelId":"us.amazon.nova-2-lite-v1:0",
 "frames":4,"challengeId":"ch_…","answers":["circle","plus","moon"],"passed":false,"roundsCorrect":0,
 "valid":[true,true,true],"repaired":[false,false,false],"latencyMs":[3120,2890,3301],"errors":[null,null,null]}
```
End-of-run summary to stdout: N, pass rate + Wilson CI, round accuracy + CI, invalid rate, mean latency, and
chance lines. Attempts with any `errors` are written but excluded from the summary (same rule as §1.6).
Imports: add `backend/layers/core` and `backend/functions/agent_worker` to `sys.path` at the top of `bench.py`.

## 6. Benchmark matrix (Phase 5; stop early if credits or time run short)
| Model | K | N (challenges) | Rounds | Notes |
|---|---|---|---|---|
| nova-2-lite | 4 | 30 | 90 | Baseline; cheap |
| nova-2-lite | 1 | 20 | 60 | "Single screenshot" condition |
| nova-2-lite | 8 | 20 | 60 | More frames doesn't help |
| nova-pro | 4 | 20 | 60 | |
| claude (if enabled) | 4 | 20 | 60 | Strongest attacker; watch cost |
| ollama (local vision model) | 4 | 20 | 60 | Build It track evidence |
`make report` builds `eval/report.md` (table per cohort: N, passes, pass rate [CI], round accuracy [CI], invalid %,
mean latency) + human cohorts from `/v1/stats` + the chance lines + conditions (date, model ids, K, prompt version).

## 7. Stretch: bespoke optical-flow attacker (`redteam/flow_solver.py`), only if ≥ 2 h buffer
Purpose: show the honest boundary ("a custom solver can beat it") and quantify its cost. Design: for frames t, t+1
build binary images; for each of 25 displacements d ∈ [-2,2]² count matches `B_t & shift(B_{t+1}, -d)` in 9×9
blocks; per block take argmax d; the two dominant displacements are figure/ground; the block mask with the
less-frequent displacement ≈ shape; classify by IoU against the 8 shapes over rotations −30…30° (use
`mdg.inside_shape`). Report its pass rate as cohort `agent:flow-solver:k8`. In the writeup: "general-purpose agents:
~chance; purpose-built solver: X%, which took Y hours to write". That honesty scores on Learning and Impact.

## 8. Cost guard
- Daily cap `AGENT_RUNS_DAILY_CAP` (default 300) enforced by DynamoDB counter → 429.
- Default model `nova-2-lite`, K=4. Claude-class models: N ≤ 20.
- Budget alarm (Phase 0). Check Billing → Bedrock after the matrix and note the cost in MEMORY.md › Metrics.
