# PLAN.md — PACT build plan (single source of truth for sequencing)

## Goal
Win on all three one-submission tracks (**Ship It**, **Build It**, **Best UI**) plus the **blog side quest**, by
shipping one thing that works end to end and is *visibly* AWS in a 3-minute video:
a human passes, an AI agent fails, Cedar decides, all on AWS, with honest numbers.

## Timeline (IST). Assumes the deadline is **Sun 20 Sep 23:59 IST**. Confirm it (see Compression if it's earlier).
| Phase | Window (IST) | Budget | Exit gate (all must be true) | File |
|---|---|---|---|---|
| **0 Setup & preflight** | Sat 16:00–17:00 | 1 h | doctor OK · scaffold copied · 20 backend tests green · frontend builds · Bedrock smoke call OK (or fallback logged) · Amplify URL known · repo pushed | `docs/phases/PHASE_0_SETUP.md` |
| **1 Backend core + deploy** | Sat 17:00–21:00 | 4 h | stack deployed · `make smoke` green: challenge → answers → token → booking ALLOW; replay DENY; no token 401 | `docs/phases/PHASE_1_BACKEND_CORE.md` |
| **2 Frontend + Amplify → M1** | Sat 21:00–01:00 | 4 h | **M1:** on the live URL a human passes 3 rounds and books; failure path + mobile OK; study link sent | `docs/phases/PHASE_2_FRONTEND_M1.md` |
| — sleep — | Sun 01:00–08:00 | | Friends do the study link overnight/morning | |
| **3 Red team → M2** | Sun 08:00–12:00 | 4 h | **M2:** Lab page runs a Bedrock agent that visibly fails; scoreboard live · **early submission done** | `docs/phases/PHASE_3_REDTEAM_M2.md` |
| **4 Accessible path + Build It local** | Sun 12:00–15:00 | 3 h | account path books with quota · full stack runs on localhost · Ollama agent fails locally · Cedar demo | `docs/phases/PHASE_4_ACCESSIBLE_AND_LOCAL.md` |
| **5 Evaluation + polish** | Sun 15:00–18:30 | 3.5 h | `eval/report.md` real numbers + CIs · Best-UI pass · About page · final README · hardening | `docs/phases/PHASE_5_EVAL_AND_POLISH.md` |
| **6 Video + submission** | Sun 18:30–22:30 | 4 h | video ≤ 3:00 on YouTube · writeup · blog · compliance checklist · submitted | `docs/phases/PHASE_6_DEMO_AND_SUBMIT.md` |
| Buffer | Sun 22:30–23:59 | 1.5 h | Re-check submission form, repo public, video plays logged-out | |

**Early submission rule:** at M2 (target Sun 12:00) submit repo + a rough 60–90 s video + draft writeup. The form is
editable until the deadline, so this guarantees a valid entry even if something later goes wrong.

## Milestones
- **M1: human path live.** Challenge → 3 rounds → token → Cedar ALLOW → booking card, on the Amplify URL, on a phone.
- **M2: AI fails live.** Lab: pick a Bedrock model → run → "What the AI saw" frames (noise) → wrong answers → FAIL;
  scoreboard shows humans vs agents.

## Critical path
Phase 0 Bedrock/AWS access → Phase 1 deploy → Phase 2 widget → Phase 3 worker → Phase 6 video.
Accessibility, local Build It, CI and polish hang off the critical path. Protect it.

## What judges must see (feature → video beat → phase)
| Judging criterion | What proves it | Video beat (docs/DEMO_VIDEO.md) | Phase |
|---|---|---|---|
| Idea & Impact | Tatkal-style bot problem + CAPTCHAs now beaten by agents; who benefits | 0:00–0:20 | 5, 6 |
| Execution ("does it work?") | Live human pass → booking; replay denied | 0:20–1:05 | 1, 2 |
| Built on AWS (Ship It: architecture + cost) | Amplify, API GW, Lambda, DynamoDB, S3, Secrets Manager, Cognito, **Bedrock** on screen; cost < $X | 1:05–2:15 | 1–4 |
| Build It (open source) | Strands Agents + Cedar + SAM CLI + DynamoDB Local/LocalStack + Ollama, all on localhost | 2:15–2:40 | 4 |
| Best UI | Polished widget + Lab + scoreboard, responsive, accessible | whole video | 2, 5 |
| Learning | Writeup + blog "what we learned" (perception gap, Cedar, Strands, SAM) | writeup | 6 |
| Demo video | ≤ 3:00, AWS visible, honest limitations | all | 6 |

## Cut list (cut from the top; never cut the bottom block)
1. `redteam/flow_solver.py` bespoke-attacker stretch
2. GitHub Actions CI
3. LocalStack profile (keep DynamoDB Local)
4. Extra benchmark cells (K=1, K=8); keep K=4 for every model
5. About-page polish beyond: figure + architecture + limitations
6. Account-path UI polish (keep it functional and shown)
7. Ollama benchmark size (keep one local run for the Build It beat)
**Never cut:** M1, M2, Cedar ALLOW/DENY visible, early submission, video, writeup, repo public, submission.

## Compression (if the deadline is earlier than Sun 23:59 IST)
- Deadline ≥ Sun 18:00: merge Phases 4 and 5 (2 h total: account path + DynamoDB Local + report), video at T-4h.
- Deadline ≥ Sun 12:00: skip Phase 4 local LocalStack and CI; do only `sam local` + Ollama in 45 min; video at T-3h.
- Deadline Sat night: ship M1 + a minimal Lab (one Bedrock model, K=4) + video. Say so in MEMORY.md › Decisions.

## Parallelism (teams of 2–4)
- Person A (backend/infra): Phases 1, 3 (worker), 4 (local). Person B (frontend): Phases 2, 3 (Lab UI), 5 (polish).
- Person C (story): study recruitment, README/About copy, blog draft, video script and recording.
- One Claude Code session per person on separate branches; merge at M1 and M2; one owner edits MEMORY.md.
