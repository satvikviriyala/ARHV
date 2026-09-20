# PHASE SPRINT: physical-first ARHV, shipped by 20:00 IST (Sun 20 Sep 2026)

**This file supersedes the Sunday rows of the PLAN.md timeline and Phases 3–6 for today.** Phases 0–2 still
define *how* to build each piece; this file defines *what* ships, in *which order*, and what gets cut.
**Read first (in this order):** `docs/PHYSICAL.md` (the thesis + `imu-v1` protocol), `docs/API.md` (family
param, trace answers, handoffs), `docs/BACKEND.md` §2–3 (imu additions), `docs/FRONTEND.md` §13 (physical path),
`docs/DEMO_VIDEO.md` (the script you are building towards), `MEMORY.md` (Snapshot, Human-Blocked).

## 0. What already exists (done by the planning session, tested; do not rewrite)
| File | State |
|---|---|
| `backend/layers/core/pact_core/imu.py` | `generate_challenge(seed)`, `verify(challenge, challenge_id, trace) -> ImuResult(passed, reasons, metrics)`, `tilt_from_gravity` |
| `redteam/imu_sim.py` | `physical_trace(...)` (physics-consistent synthetic phone) + 4 spoofs |
| `backend/tests/test_imu.py` | 21 tests (incl. the attestation-gap test that *must* keep passing) |
| `pact_core/tokens.py` | `assurance="physical"`, optional `proof=` → claim `prf` |
| `cedar/policies.cedar` + schema | `permit-physical-book` (+ tests in `test_authz.py`) |
| `scripts/imu_attack_demo.py` | offline table, or `--api <url>` against the deployed API |
| `scripts/cedar_demo.py` | includes the physical row |
| `backend/template.yaml` | CORS header `x-pact-poll-key`; routes `POST /v1/handoffs`, `GET /v1/handoffs/{handoffId}` on ApiFunction |
| `frontend/src/lib/imu.ts` (+ test) | `requestMotionPermission`, `ImuRecorder`, `TargetTracker`, types |
| `frontend/src/components/TiltChallenge.tsx` | full tilt UI; `onDone(trace)` |
Local gate right now: `make test-backend` → 40+ pass; `cd frontend && npx vitest run` → 4 pass.

## 1. Sprint rules
- Timebox every block. Overrun > 15 min → take that block's **fallback** and log it in `MEMORY.md › Decisions`.
- `main` stays demo-able; commit after each numbered task; update `MEMORY.md` (Log + Snapshot + Next Steps).
- Public name in UI, README, video, writeup: **ARHV** (Agent-Resistant Human Verification). Code identifiers
  (`pact_core`, `x-pact-token`, `pact-dev`, Cedar `Pact::`) stay unchanged. Never "IRCTC" in the UI.
- Never trust the client's "done": the server re-derives the challenge from `seedHex` and runs `imu.verify`.
- Never store or log raw sensor traces. Log `imu_verified` with `reasons` + `metrics` only.
- Numbers in README/video/writeup come only from runs you did (`eval/`, `/v1/stats`, command output you saw).

## 2. Blocks
### S0 · 15:45–16:05 · Unblock and close Phase 0
Human first (`docs/HUMAN_STEPS.md` #0): attach **AdministratorAccess** to IAM user `liv28` (Console → IAM →
Users → liv28 → Add permissions → Attach policies directly). Then:
1. `aws sts get-caller-identity` · `make doctor` · `make test` → green.
2. Amplify basic auth off (it returns 401 today):
   `aws amplify update-app --app-id d1i6xn1rxjcnkk --no-enable-basic-auth --region us-east-1` and
   `aws amplify update-branch --app-id d1i6xn1rxjcnkk --branch-name main --no-enable-basic-auth --region us-east-1`.
3. Add the Makefile target (the planning session could not write the Makefile):
   ```make
   imu-demo: ## Phone-tilt (imu-v1) attack table: offline, or against the API with IMU_API=<url>
   	$(BIN)/python scripts/imu_attack_demo.py $(if $(IMU_API),--api $(IMU_API),)
   ```
   (tab-indented recipe; add `imu-demo` to `.PHONY`). `make imu-demo` must print the 6-row table.
4. `MEMORY.md › Decisions`: "imu-v1 physical proof family added (thesis: digital-only tests are a losing race;
   vendor attestation is the endgame). Public name ARHV ('PACT' = Private Access Control Tokens, the June 2026
   Cloudflare/Chrome/Firefox/Edge anti-bot protocol, collides)."
   Commit `chore: close phase 0; adopt physical-first sprint`. Tag `phase-0-done`.
**Fallback:** still no IAM fix at 16:05 → do S1 code + tests locally (no deploy) and keep asking the human.

### S1 · 16:05–17:20 · Backend (both proof families) + deploy + smoke
Follow `docs/phases/PHASE_1_BACKEND_CORE.md` tasks 1.1–1.11 with these changes:
1. `store.put_challenge(..., answers=None, handoff_id=None)`; the imu challenge stores `family`, `seedHex`,
   `cohort`, `status`, times (and `handoffId` when present). Nothing else.
2. `functions/api/app.py` `create_challenge`: `family = body.get("family", "mdg-v1")`; unknown → 400 `bad_family`.
   `imu-v1` → `ch = imu.generate_challenge(seed)`; return 201 `{"challengeId", "expiresAt", **ch}` (targets are
   public instructions by design). Handoff fields → see S5 (return 501 `not_implemented` until then).
3. `answer_challenge`: consume first (single use), then branch on `rec["family"]`:
   - `mdg-v1`: unchanged.
   - `imu-v1`: body must be `{"trace": {...}}` (dict; ≤ 4,000 samples; raw body ≤ 512 KB else 400 `too_large`).
     `challenge = imu.generate_challenge(bytes.fromhex(rec["seedHex"]))`; `res = imu.verify(challenge, cid, trace)`;
     `store.record_attempt(cohort, family="imu-v1", passed=res.passed, rounds_correct=res.metrics.get("targetsReached", 0),
     rounds_total=3, duration_ms=res.metrics.get("durationMs", 0))`; log `imu_verified` (cid, passed, reasons,
     metrics). Pass → `tokens.mint(..., assurance="physical", challenge_id=cid, proof="imu-v1")` → 200
     `{"passed": true, "token", "expiresIn": 120, "assurance": "physical", "proof": "imu-v1", "metrics"}`.
     Fail → 200 `{"passed": false, "reasons", "metrics"}`.
4. `get_stats`: `?family=mdg-v1|imu-v1` (default `mdg-v1`); `chance` is `null` for `imu-v1`.
5. `health`: `"families": ["mdg-v1", "imu-v1"]` (keep `"family": "mdg-v1"` for compatibility).
6. Handoff routes: 501 `not_implemented` for now (S5 implements them).
7. Tests (`test_api.py`): imu create → public shape (family, nonce 32 hex, 3 targets); answer with
   `imu_sim.physical_trace` → token with `asr == "physical"`, `prf == "imu-v1"`; `orientation_only_spoof` → 200
   `passed:false` with `"gravity" in reasons`; second submit → 409; mdg tests unchanged.
8. `scripts/smoke.py`: add step **imu**: create imu challenge → `physical_trace` → answers → token `asr=physical`
   → `POST /v1/demo/bookings` 201 with `policy == "permit-physical-book"` → replay → 403 → explain shows
   `DENY` + `forbid-token-replay`.
9. Agent worker: stub (Phase 1 task 1.8). Agent-run routes: 501. The red team runs through `make bench` (S3).
10. `make lint && make test-backend` → `make deploy` → `make smoke` green. Commit, tag `phase-1-done`.
**Fallback:** deploy fails → `docs/SELF_CORRECTION.md` playbooks; at 17:20 with no stack, stop polishing and
take the smallest failing resource out (never Cedar/authorizer/booking/ApiFunction/DynamoDB/Secrets).

### S2 · 17:20–18:25 · Frontend: Home (two proofs) + `/phone` + Amplify, tested on a real phone
Build per `docs/FRONTEND.md` §13 (physical path) and the minimum of §2–5:
1. `config.ts`, `lib/api.ts` (`createChallenge({family, cohort})`, `submitAnswers`, `submitTrace`, `book`,
   `explain`, `stats(family)`), `lib/cohort.ts`, `lib/jwt.ts`.
2. `components/PhysicalWidget.tsx` (create imu challenge → `TiltChallenge` → `submitTrace` → passed/failed with
   human-readable reasons + "Try again"); `components/MdgCanvas.tsx`, `ShapeOptions.tsx`, `PactWidget.tsx`
   (motion puzzle); `BookingCard.tsx`; `DevPanel.tsx` (claims incl. `asr`/`prf`, imu metrics, explain).
3. `pages/Home.tsx`: thesis hero + Rush Hour Counter (demo) → **VerifyChooser**: "Tilt your phone (physical
   proof)" first on devices with motion sensors; "Spot the shape (motion puzzle)" first on laptops, with a QR
   (`qrcode` npm) to `/phone` so a laptop visitor can switch to the phone.
4. `pages/Phone.tsx` at `/phone`: mobile-first counter + PhysicalWidget + BookingCard (+ handoff mode in S5).
5. `npm run lint && npx vitest run && npm run build` → `make web-env && make web-deploy`.
6. **Real phone test on the Amplify HTTPS URL** (sensors need HTTPS): iPhone Safari (tap → both permission
   prompts → Allow) and any Android Chrome. Pass 3 times on each phone you have. If a real phone fails, read
   `metrics` in the DevPanel and apply `docs/PHYSICAL.md §3 Tuning knobs` (loosen only the failing rule, add a
   regression test with those metrics, `make deploy`). Log what you changed and why.
**Fallback:** Amplify serving HTML for JS/CSS or 401 → don't upload zips by hand (the hand-made `pact-web.zip` was
nested, and the catch-all rewrite then served `index.html` for every asset). Run `make web-bootstrap` (it
re-applies the asset-safe SPA rewrite to the existing app `d1i6xn1rxjcnkk`) then `make web-deploy` (zips
`frontend/dist` with `index.html` at the root). Check: `curl -sI https://main.d1i6xn1rxjcnkk.amplifyapp.com/assets/<file>.js`
→ `content-type: application/javascript`. Motion sensors need HTTPS, so never test the phone on plain `http://`.

### S3 · 18:25–18:50 · Evidence (real numbers only)
1. `make bench BACKEND=bedrock MODEL=nova-2-lite K=4 N=10` (agent vs `mdg-v1`) → `eval/results/*.jsonl`;
   add `MODEL=nova-pro` if time. Infra errors are not agent failures; label cohorts honestly.
2. `make imu-demo IMU_API=$(.venv/bin/python scripts/stack_output.py ApiUrl)`
   → the live attack table (screen-record it for the video).
3. `make cedar-demo` (screen-record). `make report` → `eval/report.md`.
4. Human pilot: 3 people on their own phones via `https://…/phone?cohort=study` + the motion puzzle on a laptop
   with `?cohort=study`. Report exact counts, no rounding up.
5. `README.md` from `docs/SUBMISSION.md §3` (ARHV name, thesis first, real numbers, honest limitations, credits).

### S4 · 18:50–19:45 · Video, writeup, submit (hard stop 19:45; 15 min buffer)
1. Record per `docs/DEMO_VIDEO.md` (≤ 2:55). The phone beat needs two angles: phone screen recording + a hand
   shot of the tilt (the physicality *is* the point).
2. Upload to YouTube (Public or Unlisted), check it plays logged-out.
3. Writeup from `docs/SUBMISSION.md §2`; AI tools list; compliance checklist; repo public; submit by **19:45**.

### S5 · Stretch (only if S2's gate passed by 17:50) · Laptop → phone handoff
Implement `docs/PHYSICAL.md §4` / `docs/API.md` handoff routes: `store.create_handoff`, `bind` at challenge
creation, `verify_handoff` on pass, `deliver_handoff` on poll; laptop `VerifyChooser` shows the handoff QR and
polls `GET /v1/handoffs/{handoffId}` with `x-pact-poll-key` every 1.5 s; phone shows "Done. Return to your
computer." Tests: wrong phone key → 404; token delivered once; expired → 410. Video beat upgrade: laptop books
with a token earned by tilting the phone.

## 3. Cut list for today (cut from the top; never cut the bottom block)
1. Lab page + cloud worker (the red team runs via `make bench`; show its output in the video)
2. Handoff (S5) — the phone books on its own instead
3. Cognito account UI (the function + Cedar quota policy ship; show `make cedar-demo` rows; say so honestly)
4. LocalStack/Ollama local path (keep `make cedar-demo` offline for the Build It beat; `sam local` only if time)
5. About page (README + DevPanel carry the explanation), blog, CI, human study beyond the pilot
**Never cut:** deployed API + Cedar ALLOW/DENY visible · phone-tilt pass on a real phone · spoof table ·
motion puzzle human pass · Bedrock agent result (real numbers) · video with AWS visible · writeup · submission.

## 4. Gate (all true before S4)
- [ ] `make smoke` green on the deployed stack, including the imu step
- [ ] On the Amplify URL, a real phone passes the tilt check and books (`permit-physical-book`)
- [ ] `make imu-demo IMU_API=…` prints the table against the live API
- [ ] `eval/results/` has a real Bedrock run; `eval/report.md` regenerated
- [ ] README names ARHV, states the thesis, the attestation gap and the limitations honestly
