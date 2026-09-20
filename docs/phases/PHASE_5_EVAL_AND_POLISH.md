# PHASE 5: Evaluation + polish (budget 3.5 h · Sun 15:00–18:30 IST)

> **Sun 20 Sep:** reduced to sprint block **S3** (bench run, live spoof table, 3-person pilot, README).

**Goal:** real numbers with confidence intervals, a UI that wins "Best UI", a README a judge understands in 60 s,
and a hardened deployment.
**Read first:** `docs/EVALUATION.md`, `docs/REDTEAM_AGENT.md §6–8`, `docs/SECURITY.md`, `docs/SUBMISSION.md §3`,
`docs/FRONTEND.md §7, §9`.

## Tasks
**5.1 Benchmark matrix** (cloud API, sequential, `--sleep 1`): run the cells of docs/REDTEAM_AGENT.md §6 in order
(nova-2-lite K4 N30 → nova-2-lite K1 N20 → nova-2-lite K8 N20 → nova-pro K4 N20 → claude K4 N20 if enabled). Watch
for throttling; stop early if time or cost demands (log the cut). Commit the JSONL files.

**5.2 Report.** Implement `redteam/report.py` (reads `eval/results/*.jsonl` + `GET /v1/stats`; uses
`pact_core.stats.wilson`) → `make report` → `eval/report.md` with the sections in docs/EVALUATION.md §6. Copy the
key rows into MEMORY › Metrics (with source). Check the study cohort N (target ≥ 10 people); nudge the human (H7)
if it's low.

**5.3 About page + README.** About per docs/FRONTEND.md §7 (copy the figure to `frontend/public/`). README per
docs/SUBMISSION.md §3 with the real results table, mermaid architecture, run instructions, limitations, AI tools,
credits and licences. Numbers are copied from `eval/report.md`.

**5.4 Best-UI pass** (desktop 1440 px + phone 360 px): typography scale, spacing rhythm, consistent radii, empty/
loading/error states everywhere, focus styles, motion 150–200 ms, no layout shift when the canvas loads, favicon +
`<title>` + meta description + Open Graph image (the figure). Optional: Lighthouse accessibility ≥ 90.

**5.5 Hardening:** docs/SECURITY.md §5 checklist (CORS exact, secret grep, `ReauthorizeEvery: 0`, throttling, cap,
S3 private, limitations in README). Redeploy backend + frontend; `make smoke` green.

**5.6 Optional (only with ≥ 2 h buffer, in this order):** GitHub Actions CI (docs/TESTING.md §7); `redteam/flow_solver.py`
stretch (docs/REDTEAM_AGENT.md §7).

**5.7 Close.** Tests + lint green · MEMORY · `git tag phase-5-done` · push.

## Exit gate
- [ ] `eval/report.md` generated from committed JSONL + live stats; human (study) N and agents N stated with CIs
- [ ] README final (results, architecture, limitations, AI tools, credits) · About page complete
- [ ] UI checklist done on phone + desktop · security checklist ticked · smoke green after redeploy
