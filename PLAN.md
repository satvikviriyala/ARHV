# PLAN.md — ARHV (codename PACT) build plan (single source of truth for sequencing)

## Goal
Win on all three one-submission tracks (**Ship It**, **Build It**, **Best UI**) with one thing that works end to
end and is *visibly* AWS in a 3-minute video, built around one thesis:

> **Digital-only human verification is a capability race that agents win. The durable boundary is physical:
> prove a human just moved a real device, for this request. Browsers can't attest sensors yet, so vendors
> must, the way TPM 2.0 became mandatory for Windows 11.** (Full argument: `docs/PHYSICAL.md`.)

What the video proves: a human passes the **phone-tilt physical check** (`imu-v1`) and books; cheap sensor spoofs
are rejected by server-side physics; a physics-perfect simulator still passes (the honest attestation gap that
motivates vendor support); on the perceptual tier (`mdg-v1`) a Bedrock agent fails where humans pass; Cedar on
AWS decides every booking; honest numbers.

## Augmentation (HIGH PRIORITY, Sun 20 Sep): physical-first
| Tier | Family | Today |
|---|---|---|
| T0 perceptual | `mdg-v1` motion-defined glyph | build (Phases 1–2) |
| **T1 physical, unattested** | **`imu-v1` phone tilt path, physics-verified server-side** | **core + tests + Cedar + UI component done; integrate in the sprint** |
| T2 physical, vendor-attested | `navigator.physical.request(...)` proposal (tilt / lid angle / touch presence) | documented proposal + roadmap |
| Accessible | Cognito account path (quota) | function + Cedar policy; UI cut today if needed |
MacBook hinge: **roadmap only** (no public lid-angle API; M1/M2 Macs lack the sensor). Fingerprint presence:
**roadmap via WebAuthn user verification**. Both are the strongest *examples* of why vendor support is needed.

## Timeline (IST). Deadline **Sun 20 Sep 2026, 20:00 IST** (MEMORY.md › Snapshot). Submit by 19:45.
Saturday's Phases 0–2 slipped (IAM + Amplify). **Today runs on `docs/phases/PHASE_SPRINT_TO_2000.md`:**
| Block | Window (IST) | Exit gate | Detail |
|---|---|---|---|
| **S0 Unblock** | 15:45–16:05 | liv28 has AdministratorAccess · tests green · Amplify basic auth off · `imu-demo` target | sprint §S0 |
| **S1 Backend + deploy** | 16:05–17:20 | stack deployed · `make smoke` green incl. the imu step (physical token → ALLOW; replay → DENY) | sprint §S1 + PHASE_1 |
| **S2 Frontend + Amplify** | 17:20–18:25 | on the Amplify URL a real phone passes the tilt check and books; motion puzzle works on a laptop | sprint §S2 + PHASE_2 |
| **S3 Evidence** | 18:25–18:50 | Bedrock bench run · live spoof table · Cedar table · 3-person pilot · README | sprint §S3 |
| **S4 Video + submit** | 18:50–19:45 | ≤ 3:00 video on YouTube · writeup · compliance checklist · **submitted** | sprint §S4 + PHASE_6 |
| Buffer | 19:45–20:00 | re-check form, repo public, video plays logged-out | |
| S5 Stretch | only if S2 passed by 17:50 | laptop → phone handoff (QR) | sprint §S5 |
Early-submission rule still applies: the moment S2's gate passes, submit repo + a 60 s rough video + draft writeup
(the form is editable until the deadline), then improve.

## Milestones
- **M1: humans pass, on AWS.** Phone tilt → physical token → Cedar ALLOW → booking card on the Amplify URL; the
  motion puzzle passes on a laptop.
- **M2: the machines fail, honestly.** Live spoof table (5 rejected, simulator passes = attestation gap) and a
  Bedrock agent's real `mdg-v1` numbers with 95% CIs.

## Critical path
IAM fix → S1 deploy → S2 phone test on HTTPS → S3 evidence → S4 video. Everything else hangs off it.

## What judges must see (feature → video beat → block)
| Judging criterion | What proves it | Video beat (docs/DEMO_VIDEO.md) | Block |
|---|---|---|---|
| Idea & Impact | agents beat screen puzzles; physical proof + vendor attestation is the durable answer; Tatkal-style rush as the motivating case | 0:00–0:20, 2:05–2:35 | S4 |
| Execution | real phone passes and books; spoofs rejected by the live API; replay denied | 0:20–1:05 | S1–S3 |
| Built on AWS | Amplify, API Gateway + Lambda authorizer, Lambda, DynamoDB, Secrets Manager, Bedrock (Strands), CloudWatch Cedar logs | 1:25–2:05 | S1–S3 |
| Build It (open source) | Cedar policies (offline `make cedar-demo`), Strands Agents, SAM CLI, open verifier + simulator | 1:05–1:25, 2:35–2:50 | S3 |
| Best UI | marble-on-a-plate tilt UI, motion puzzle, DevPanel, mobile-first | whole video | S2 |
| Learning | writeup: why digital tests lose, what physics can and can't prove, Cedar/Strands/SAM lessons | writeup | S4 |

## Cut list (today; cut from the top; never cut the bottom line)
1. Lab page + cloud agent worker (use `make bench`) 2. Laptop → phone handoff (S5) 3. Cognito account UI
4. LocalStack/Ollama local path (keep offline `make cedar-demo`) 5. About page, blog, CI, study beyond a pilot
**Never cut:** deployed API + Cedar ALLOW/DENY · real-phone pass · spoof table · human motion-puzzle pass ·
real Bedrock numbers · video with AWS visible · writeup · submission.

## Saturday plan (historical; phase files remain the how-to reference)
Phases 0–6 in `docs/phases/PHASE_*.md` define implementation detail for each component. Phase 3 (Lab + worker),
Phase 4 (account UI + local stack) and Phase 5 (full study) are reduced by the sprint cut list above.
