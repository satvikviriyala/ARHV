# EVALUATION — does PACT separate humans from agents? (honest, small-N, with intervals)

## 1. Hypotheses
- **H1 (humans):** people pass `mdg-v1` on the first or second try; round accuracy ≥ 90%.
- **H2 (agents):** screenshot-driven vision agents answer at chance (1/6 per round); pass rate ≈ 0.46%.
- **H3 (more frames don't help):** agent accuracy with K = 8 isn't meaningfully above K = 1.
Report what the data says, including if a hypothesis fails.

## 2. Cohorts and how they're produced
| Cohort | Who | How |
|---|---|---|
| `study` | known humans (friends, classmates) | open `https://<amplify-url>/?cohort=study`, do 1–2 challenges, no practice |
| `public` | anyone else on the site (includes us testing) | default; reported separately, not used for H1 |
| `agent:<alias>:k<K>` | Bedrock models via Lab/worker or bench CLI | `docs/REDTEAM_AGENT.md` |
| `agent:ollama-<model>:k<K>` | local vision model | bench CLI against local or cloud API |
Cohort labels are self-declared (header/query). That's fine for a study you control; say so in the report.

## 3. Human study protocol (runs Sat night → Sun afternoon)
- Target **N ≥ 10 people**, ≥ 15 challenges. Recruit via WhatsApp with this message (human step H6):
  > "Quick favour (30 seconds, anonymous): open <URL>/?cohort=study on your phone or laptop, click 'Book the last
  > seat' and solve the puzzle once (twice if you like). No sign-up, nothing personal is stored. Thanks!"
- No coaching beyond the on-screen instructions. Don't pre-train participants. Don't include the builders in `study`
  (use `public`).
- Stored per attempt: cohort, pass/fail, rounds correct, total time. No personal data.

## 4. Agent benchmark
Matrix and commands: `docs/REDTEAM_AGENT.md §6`. Run it Sunday afternoon (Phase 5) after the pilot (Phase 3) confirms
the pipeline. Exclude infra-error attempts (logged separately).

## 5. Statistics (keep it simple and correct)
- Proportions with **Wilson 95% intervals** (`pact_core.stats.wilson`): pass rate over challenges, round accuracy
  over rounds.
- Compare agents with chance: is 1/6 inside the round-accuracy CI? For H3 compare K=1 vs K=8 CIs (overlap ⇒ no
  evidence of improvement).
- Never report a percentage without N. With N = 20 and 0 passes, the 95% upper bound is ≈ 16%: say "0/20 (95% CI 0–16%)",
  not "0%".
- Human time: report the mean from `durationMsTotal / attempts` (median needs raw data, so skip it).

## 6. Report (`make report` → `eval/report.md`)
Sections: **Setup** (dates, puzzle version `mdg-v1` + parameters, model ids, K, prompt version, N) · **Results
table** (cohort, attempts, passes, pass rate [CI], rounds, round accuracy [CI], invalid %, mean latency/time) ·
**Chance lines** · **Findings** (3 bullets, plain) · **Limitations** (small N, self-declared cohorts, generous
attacker, bespoke-solver caveat) · **Reproduce** (exact commands). Put the key numbers into `MEMORY.md › Metrics`,
the README and the writeup, **copied from the report**, never retyped from memory.

## 7. Decision rules during the weekend
- Phase 2 pilot (≥ 3 humans): if any human fails twice in a row, apply `docs/CHALLENGE_MDG.md §7` before M1.
- Phase 3 pilot (≥ 20 agent rounds): if a model's round-accuracy lower CI bound > 0.25, tune (§7 there) and re-run
  both pilots. Log it.
- If a strong model genuinely beats the puzzle and tuning doesn't fix it, **don't hide it**: report it, reframe the
  claim ("defeats model X, not model Y"), and show it in the Lab. Honest results beat a fake 0%.
