# SECURITY — threat model, controls, and honest limitations

## 1. Assets
The protected action (a scarce seat), the token-signing key, the integrity of the pass/fail decision, the
honesty of the published numbers, and the AWS bill.

## 2. Threats → controls
| Threat | Control | Where |
|---|---|---|
| Screenshot-driven AI agent (computer-use / browser agents) | Answer exists only in motion; single frames are uniform noise (tested) | `mdg.py`, `test_single_frame_carries_no_shape_signal` |
| Reading the answer from the client | Answers, seed and specs never sent; only frames + options | `generate_challenge()["public"]`, API test |
| Predicting the generator (RNG state recovery) | Keyed SHAKE-256 streams (`KeyedRng`), 32-byte secret seed per challenge | `mdg.py` |
| Random guessing | 3 rounds × 6 options → 0.46% chance; single-use challenge; 180 s expiry | `mdg.py`, `store.consume_challenge` |
| Replaying a challenge answer | Conditional update `issued → answered` | `store.py` |
| Token theft/replay | 120 s TTL, `jti` single use (conditional put), Cedar `forbid-token-replay`, token in memory only | authorizer, Cedar |
| Token forgery | HS256 with a 64-char key generated into Secrets Manager; `iss`/`aud`/`exp`/required claims checked | `tokens.py` |
| Cached authorizer decisions | `ReauthorizeEvery: 0` (tested) | `template.yaml` |
| Authorizer crash = open door | Catch-all → deny (fail closed); API Gateway returns 500 on authorizer errors anyway | authorizer |
| Cedar request injection via ids | Dict-form entity references; ids validated by regex | `authz.py`, `ids.py` |
| Abuse / cost blow-up | Stage throttling 25 rps/burst 50; agent-run daily cap (DynamoDB counter); budget alarm; S3 lifecycle | template, store |
| Account path abuse | Cognito email verification + Cedar daily quota (2) | Cognito, Cedar |
| Secrets leakage | No secrets in git/logs/chat; Claude Code denied `secretsmanager get-secret-value` and `~/.aws/credentials` | `.claude/settings.json` |
| Least privilege | Per-function SAM policy templates; only the worker can call Bedrock; only ExplainFunction is read-only | template |
| **Physical (`imu-v1`):** screen-only agent | Needs a live accelerometer + gyroscope + orientation stream that follows a fresh random path | `imu.verify` |
| Forged "done" from the client | Server re-derives the challenge from `seedHex` and verifies the raw trace; the client never decides | `api/app.py`, `imu.py` |
| Orientation-only sensor emulation (DevTools, automation) | Gravity magnitude (≥ 80% of samples 7.5–12.5 m/s²) + tilt-vs-gravity consistency | `imu.py` (`gravity`, `tilt`) |
| Dead/random gyroscope | Per-axis correlation of orientation rate vs `rotationRate` ≥ 0.5 | `imu.py` (`gyro`) |
| Scripted teleporting input | ≤ 30° per sample and ≤ 900°/s | `imu.py` (`continuity`) |
| Replay of a genuine recording | Fresh 128-bit nonce + random targets (8 directions × 16–26°), single-use challenge, 180 s expiry | `imu.py` (`binding`, `targets`), store |
| Stitched / fast-forwarded traces | Monotonic time, median sample interval 8–120 ms, max gap 750 ms, duration bounds | `imu.py` (`timing`) |
| Oversized payloads | ≤ 4,000 samples; raw body ≤ 512 KB checked before parsing | `imu.py`, `api/app.py` |
| Motion data as a fingerprint (privacy) | Raw traces never stored or logged; only summary metrics in `imu_verified` logs and stats | `api/app.py`, DATA_MODEL |
| Physics-aware sensor simulator | **Not stopped by the web tier** (tested and shown). Closed only by vendor attestation (`docs/PHYSICAL.md §7`) | limitation #7 |
| Handoff abuse (stretch) | 128-bit poll/phone keys, hashes only, 300 s TTL, token delivered once (conditional update), same 404 for wrong id or key | `store.py` |

## 3. Logging hygiene
Log `challengeId`, `jti`, `runId`, decisions, policy ids, cohorts, latencies, imu `reasons` + `metrics`. Never log
tokens, seeds, human challenge answers, **raw sensor samples**, handoff keys, emails or the secret. Agent answers and truth for *agent* runs are fine to log.

## 4. Honest limitations (put these in the README, About page and writeup; they earn trust)
1. **A bespoke solver can beat `mdg-v1`.** An optical-flow program written for this puzzle (block matching →
   segment → template match) can recover the shape. PACT's claim is about *general-purpose* agents, and about
   restoring the cost asymmetry: attackers must engineer per-family solvers, which family rotation and parameter
   jitter make recurring.
2. **An agent that writes code on the fly** (captures many frames via JS, then computes motion) could approach that
   bespoke solver. Not tested this weekend; stated as future work.
3. **Human CAPTCHA farms** defeat any human test, PACT included. Mitigations are economic (rate limits, quotas),
   not perceptual.
4. **Accessibility trade-off:** motion puzzles exclude some users (blind, low vision, vestibular disorders). The
   account path is weaker assurance, hence the Cedar quota.
5. **Small-N evaluation**, self-declared cohorts, one weekend. Numbers come with 95% CIs and exact conditions.
6. **Timing/behaviour signals** are recorded but not used for decisions (future work).
7. **Web sensor streams are unattested.** `imu-v1` rejects cheap spoofs, but a physics-consistent synthetic trace
   passes (we test and show it). That is the reason ARHV proposes vendor-attested physical gestures; until then
   `physical` is "sensor-assisted" assurance, not proof of a real device.
8. **Human farms can tilt real phones.** Physical proof raises cost per attempt; quotas and rate limits still matter.
9. **Motor impairments and devices without sensors** (most laptops, some in-app browsers) can't use the tilt check:
   the motion puzzle and the account path remain available.
10. **Failure reasons are returned to the client** (rules are public; Kerckhoffs). This helps honest users and our
    tuning; it also tells an attacker which check failed. A production deployment could return only `passed:false`.

## 5. Pre-submission security checklist (Phase 5)
- [ ] `AllowedOrigins` = `http://localhost:5173` + the Amplify URL only (no `*`).
- [ ] `grep -RInE "(AKIA|aws_secret|BEGIN PRIVATE|eyJhbGci)" --exclude-dir={node_modules,.venv,.aws-sam,dist} .` → nothing.
- [ ] Authorizer: `ReauthorizeEvery: 0`; fail-closed test green.
- [ ] Throttling + agent daily cap in place; budget alarm exists.
- [ ] S3 bucket private (Block Public Access all true); presigned URLs expire in 900 s.
- [ ] README has the limitations section; the UI uses a fictional brand only.
- [ ] `grep -RIn '"samples"' eval/ docs/` finds no stored real-user traces; logs contain `imu_verified` metrics only.
