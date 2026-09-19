# SUBMISSION — writeup, README, blog, AI tools, compliance

## 1. AI tools used (keep this list true; paste it into the writeup and README)
- **Claude Code** (Anthropic): implementation, tests, infrastructure-as-code and debugging, driven by the design docs in `docs/`.
- **Claude** (claude.ai): research, architecture planning and documentation drafting.
- *(Add any others the team used, e.g. GitHub Copilot or ChatGPT, with what for.)*
- Amazon Bedrock models (Nova, Claude) and Ollama models are **part of the product** (the red team), not coding tools.

## 2. Writeup template (the form's "short writeup"; ~350–500 words; fill numbers from eval/report.md)
```
PACT: human verification that AI agents can't fake

The problem. First-come-first-served public slots, like Tatkal tickets, are won by bots in the first minutes.
Indian Railways deactivated 3.03 crore suspicious user IDs in 2025 and relies on multi-level CAPTCHAs, but AI
agents now solve CAPTCHAs (100% of reCAPTCHAv2 image challenges; agents clicking "I'm not a robot") while
puzzles get harder for people. Who it helps: the student booking a ticket home, the family waiting for a slot.

What we built. A human-verification widget whose answer exists only in motion: a shape hidden in moving dots.
Humans see it instantly; any single frame (all a screenshot-driven agent gets) is statistically uniform noise
(we test this). Passing gives a 120-second single-use token; a Lambda authorizer evaluates Cedar policies
before the protected action runs. A Strands Agents red team on Amazon Bedrock attacks the same puzzle live.
Results (N, 95% CI): humans X/N (…); Nova 2 Lite Y/N (…); Claude … ; chance 0.46%.
Accessibility: a non-puzzle path through a Cognito-verified account, quota-limited by the same Cedar policies.

Where AWS fits. Amplify Hosting (app) → API Gateway HTTP API (routes, throttling, Lambda + JWT authorizers) →
Lambda on arm64 (challenge engine, Cedar authorizer, protected action, red-team worker) → DynamoDB (single-use
challenges and tokens, stats) → Secrets Manager (auto-generated signing key) → S3 (frames the AI saw) →
Cognito (accessible path) → Amazon Bedrock (Nova/Claude red team). Open source on localhost: SAM CLI, Cedar,
Strands Agents, DynamoDB Local/LocalStack, Ollama. Cost: a fraction of a cent per verification; the weekend,
including N red-team runs, cost $Z.

What we learned. (3–4 honest bullets: motion perception as a security primitive; why Mersenne Twister would have
leaked the answer; Cedar's forbid-overrides-permit; async patterns under the 30-second API limit; …)

Limitations. A purpose-built optical-flow solver can beat this puzzle; it raises attacker cost instead of being
unbreakable. Small-N study. Human CAPTCHA farms remain out of scope.

AI tools used. Claude Code (implementation), Claude (research/planning).
Links: repo · live app · video · blog.
```

## 3. README template (Phase 5 replaces the placeholder README)
Sections in order: title + one-line pitch + badges (CI if any) · **Demo** (YouTube link, live URL, GIF/figure
`docs/assets/screenshot-vs-motion.png`) · **The problem** (3 cited facts from docs/CONTEXT.md §5) · **How it works**
(3 steps + figure) · **Architecture** (mermaid from docs/ARCHITECTURE.md §1 + service list + cost) · **Results**
(table from eval/report.md, with CIs and N) · **Run it** (cloud: `make setup build deploy web-bootstrap web-env
web-deploy`; local: `make local-up local-api`, `make bench BACKEND=ollama …`) · **Accessibility** · **Security &
limitations** (docs/SECURITY.md §4) · **What we learned** · **AI tools used** · **Credits & licences** · **License** (MIT).
Credits to list (with licence): React, React Router, Vite, Tailwind CSS (MIT) · AWS Amplify JS + UI (Apache-2.0) ·
lucide (ISC) · PyJWT, pytest, ruff (MIT) · boto3, moto, cedarpy, Cedar, Strands Agents (Apache-2.0) · NumPy (BSD-3) ·
Pillow (MIT-CMU) · Inter, JetBrains Mono (OFL) · DynamoDB Local (AWS licence) · Ollama (MIT) and each local model
(licence from `ollama show <model> --license`) · research cited in docs/CONTEXT.md.

## 4. Blog (AWS Builder Center, side quest: top 5 win a keyboard)
Title: **"The CAPTCHA a screenshot can't solve: building PACT on AWS in a weekend."** 800–1,200 words:
1. The problem (Tatkal bots, agents beating CAPTCHAs), with sources. 2. The idea: motion-defined shapes and why one
frame is noise (figure). 3. Architecture on AWS (diagram; why HTTP API + Lambda authorizer + Cedar; single-table
DynamoDB; async Bedrock worker). 4. Red-teaming with Strands Agents: fairness rules and results table with CIs.
5. Build It: the same stack on localhost with SAM CLI, DynamoDB Local and Ollama. 6. What surprised us (RNG
leakage, reserved words, 30 s limit, authorizer caching). 7. Limitations and what's next. Link the repo and
video; add the blog link to the submission and README.

## 5. Social post (#BharatBuilds)
"We built PACT for #BharatBuilds First Commit: human verification AI agents can't fake. A shape hidden in moving
dots: you see it, a screenshot sees noise. Serverless on AWS (Lambda, API Gateway, DynamoDB, Cedar, Bedrock) + a
Strands red team. Video: <link> · Code: <link>"

## 6. Compliance checklist (tick every box before the final submit)
- [ ] Repo **public**; created during the event; no code from older projects; MIT `LICENSE`; credits + licences in README.
- [ ] Video on **YouTube**, **under 3:00**, Public/Unlisted, plays logged-out; **shows AWS** (Amplify URL, console cuts, Bedrock run).
- [ ] Writeup covers **problem, build, where AWS fits**; lists **all AI tools used**; numbers match `eval/report.md`.
- [ ] Every feature claimed in the writeup is **visible in the video** (otherwise remove the claim).
- [ ] Live URL works in an incognito window on a phone; the Lab runs (or the video shows a completed run).
- [ ] Blog published on AWS Builder Center and linked.
- [ ] Every team member has an AWS Builder Center profile with student verification submitted.
- [ ] Submitted on the hackathon's own form before the deadline; confirmation screenshot saved; edits done before cut-off.
- [ ] Budget alarm quiet; stack left running for judges (don't tear down until results).
