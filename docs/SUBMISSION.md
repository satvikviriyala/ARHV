# SUBMISSION — writeup, README, blog, AI tools, compliance

## 1. AI tools used (keep this list true; paste it into the writeup and README)
- **Claude Code** (Anthropic): implementation, tests, infrastructure-as-code and debugging, driven by the design docs in `docs/`.
- **Claude** (claude.ai): research, architecture planning and documentation drafting.
- **Cursor / Cursor Agent (GPT-5.6 Luna)**: accelerated implementation and integration, including testing,
  debugging, and evidence-report generation in the Cursor IDE.
- **HyperFrames**: video generation and production support for the motion-graphic clips listed in
  `docs/DEMO_VIDEO.md`.
- *(Add any others the team used, e.g. GitHub Copilot or ChatGPT, with what for.)*
- Amazon Bedrock models (Nova, Claude) and Ollama models are **part of the product** (the red team), not coding tools.

## 2. Writeup template (the form's "short writeup"; ~350–500 words; fill numbers from eval/report.md and /v1/stats)
```
ARHV: human verification for the age of AI agents, and why it has to become physical

The problem. Scarce public slots, like Tatkal tickets, are won by bots in the first minutes, and the CAPTCHAs
meant to stop them are losing: vision models solve 100% of reCAPTCHAv2 image challenges (2024) and AI agents
click "I'm not a robot" (2025), while puzzles get harder for people. Every test that lives only on a screen is a
capability race, and agents win capability races.

Our thesis. The durable boundary is physical: prove a person just moved a real device, for this request.
Browsers can't prove their sensors are real today, so the endgame is vendor-attested physical gestures, the way
Windows 11 made TPM 2.0 mandatory so security could rest on hardware.

What we built. (1) A physical proof (imu-v1): tilt your phone to roll a dot through three server-randomised
rings. The server verifies the raw accelerometer, gyroscope and orientation stream with physics (gravity
magnitude, tilt-vs-gravity, gyro-vs-orientation, continuity, timing, targets in order, nonce binding) and never
stores the trace. Emulated sensors, a dead gyro, a phone flat on a desk, teleporting input and replayed
recordings are all rejected by the live API; a physics-perfect simulator still passes. We show that on purpose:
it is exactly the gap vendors must close. (2) A perceptual proof (mdg-v1): a shape visible only in motion; any
single frame, which is all a screenshot agent sees, is uniform noise. A local-API run of the Strands Agents red
team on Amazon Bedrock (Nova 2 Lite, K=4) scored 0/20 full puzzles, with 12/60 rounds correct (95% CI
[0.1183, 0.3178]); no infrastructure-error attempts were counted. The deployed asynchronous Lab also completed
real Nova runs and visibly showed a failed verdict; no human-study count is claimed yet. (3) Either proof yields a 120-second single-use token; a Lambda authorizer
evaluates Cedar policies (permit-physical-book, permit-motion-book, forbid-token-replay, account quota) before the
protected action runs. (4) A concrete proposal: navigator.physical.request(), an OS-rendered gesture signed by
the secure sensor hub / TPM / Secure Enclave and redeemed as a private, unlinkable token, an identity-free
issuance signal for the Private Access Control Tokens browsers announced in June 2026 (lessons from Web
Environment Integrity's withdrawal: open standard, no fingerprinting, accessible alternatives).

Where AWS fits. Amplify Hosting (app) → API Gateway HTTP API (routes, throttling, Lambda + JWT authorizers) →
Lambda on arm64 (both verifiers, Cedar authorizer, protected action) → DynamoDB (single-use challenges and
tokens, stats, TTL) → Secrets Manager (auto-generated signing key) → Cognito (accessible account path) → Amazon
Bedrock (Nova red team via Strands) → CloudWatch (Cedar decision logs). Built with SAM; policies are open-source
Cedar, testable offline. Cost: a fraction of a cent per verification.

What we learned. (3–4 honest bullets: iOS and Android report gravity with opposite signs; checking physics
across sensors beats checking any one sensor; Mersenne Twister would have leaked the hidden shape; Cedar's
forbid-overrides-permit makes single-use tokens a one-line policy; …)

Limitations. Web sensor streams are unattested (a physics-aware simulator passes: we demonstrate it). Human farms
can tilt real phones (quotas and cost handle them). Motor-impaired users need the account path. A purpose-built
optical-flow solver can beat the perceptual puzzle. Small-N pilot.

AI tools used. Claude Code (implementation), Claude (research, planning, docs), and Cursor Agent (GPT-5.6 Luna;
implementation, integration, testing, debugging, and evidence reports). Bedrock models are part of the product
(the red team), not coding tools. Links: repo · live Amplify URL · video.
```

## 3. README template (replace the placeholder README in S3)
Sections in order: **ARHV** title + one-line pitch ("Agents can read any screen. They can't tilt your phone.")
· **Demo** (YouTube link, live URL, figure `docs/assets/screenshot-vs-motion.png`) · **Why physical** (the four-step
argument from `docs/PHYSICAL.md §1`, 3 cited facts from `docs/CONTEXT.md §5`) · **How it works** (tiers table
T0/T1/T2; the `imu-v1` checks table; the motion puzzle in 3 lines) · **Attack results** (the `make imu-demo` table
verbatim from the live API + the Bedrock bench table with N and CIs; say plainly that the simulator passes) ·
**The proposal** (`navigator.physical.request`, privacy principles, TPM analogy) · **Architecture** (mermaid from
`docs/ARCHITECTURE.md §1` + §1.1 tiers + service list + cost) · **Run it** (cloud: `make setup build deploy
web-bootstrap web-env web-deploy`; offline: `make test`, `make cedar-demo`, `make imu-demo`) · **Accessibility**
(account path, reduced motion) · **Security & limitations** (`docs/SECURITY.md §4`) · **Prior art** (SenCAPTCHA,
Private Access Tokens, Play Integrity/App Attest, WEI) · **AI tools used** · **Credits & licences** · **License** (MIT).
Name note for the README footer: "ARHV was developed under the codename PACT; code identifiers keep that name."
Credits to list (with licence): React, React Router, Vite, Tailwind CSS (MIT) · AWS Amplify JS + UI (Apache-2.0) ·
lucide (ISC) · qrcode (MIT) · PyJWT, pytest, ruff (MIT) · boto3, moto, cedarpy, Cedar, Strands Agents (Apache-2.0) ·
NumPy (BSD-3) · Pillow (MIT-CMU) · Inter, JetBrains Mono (OFL) · research cited in docs/CONTEXT.md and docs/PHYSICAL.md.

## 4. Blog (AWS Builder Center, side quest: top 5 win a keyboard)
Title: **"Agents can read any screen. They can't tilt your phone: building ARHV on AWS."** 800–1,200 words
(after the deadline is fine):
1. The problem (Tatkal bots, agents beating CAPTCHAs), with sources. 2. The thesis: why human verification must
become physical and vendor-attested (TPM analogy), and the phone-tilt physics checks. Then the perceptual tier:
motion-defined shapes and why one frame is noise (figure). 3. Architecture on AWS (diagram; why HTTP API + Lambda authorizer + Cedar; single-table
DynamoDB; async Bedrock worker). 4. Red-teaming with Strands Agents: fairness rules and results table with CIs.
5. Build It: the same stack on localhost with SAM CLI, DynamoDB Local and Ollama. 6. What surprised us (RNG
leakage, reserved words, 30 s limit, authorizer caching). 7. Limitations and what's next. Link the repo and
video; add the blog link to the submission and README.

## 5. Social post (#BharatBuilds)
"We built ARHV for #BharatBuilds First Commit: human verification that has to be physical. Tilt your phone
through random targets; our server checks the sensor physics; spoofs fail, and we show exactly where browsers
need vendor attestation. Serverless on AWS (Lambda, API Gateway, DynamoDB, Cedar, Bedrock). Video: <link> · Code: <link>"

## 6. Compliance checklist (tick every box before the final submit)
- [x] Repo **public**; created during the event; no code from older projects; MIT `LICENSE`; credits + licences in README.
- [ ] Video on **YouTube**, **under 3:00**, Public/Unlisted, plays logged-out; **shows AWS** (Amplify URL, console cuts, Bedrock run).
- [ ] The video shows a **real phone** passing the tilt check (screen + hand), the **live spoof table**, and says
      honestly that the simulator passes (attestation gap).
- [ ] UI, README, video and writeup use the name **ARHV**; no real organisation's name or logo in the product UI.
- [x] Writeup covers **problem, build, where AWS fits**; lists **all AI tools used**; numbers match `eval/report.md`.
- [ ] Every feature claimed in the writeup is **visible in the video** (otherwise remove the claim).
- [ ] Live URL works in an incognito window on a phone (HTTPS; tilt check passes); the motion puzzle works on a laptop.
- [ ] (Optional today) Blog published on AWS Builder Center and linked.
- [ ] Every team member has an AWS Builder Center profile with student verification submitted.
- [ ] Submitted on the hackathon's own form before the deadline; confirmation screenshot saved; edits done before cut-off.
- [ ] Budget alarm quiet; stack left running for judges (don't tear down until results).
