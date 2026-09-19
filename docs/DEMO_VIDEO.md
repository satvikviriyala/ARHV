# DEMO VIDEO — ≤ 3:00 on YouTube (aim for 2:50). "If the video doesn't show it, it doesn't count."

## 1. Script (voiceover + what's on screen). Every AWS service named must be *visible* when named.
| Time | On screen | Voiceover (tight; read at a calm pace) |
|---|---|---|
| 0:00–0:15 | Title card "PACT", then text overlays with sources: "Tatkal: bot traffic peaks in the first 5 minutes (AIR, 2025)" · "3.03 crore suspicious IRCTC IDs deactivated in 2025 (Rajya Sabha reply)" · "AI agents now click 'I'm not a robot'" | "Every day, bots beat real people to scarce slots, like Tatkal tickets. CAPTCHAs are supposed to stop them. But AI agents now solve CAPTCHAs, and the puzzles keep getting harder for humans." |
| 0:15–0:32 | The animated puzzle full-screen → pause → frozen noise frame, labelled "what an AI agent's screenshot sees" | "PACT flips it. There's a star hidden in these dots. You see it because the dots inside move together. Freeze a frame and it's pure noise, and a frame is all a screenshot-based agent gets." |
| 0:32–1:02 | Browser with the **Amplify URL visible**: Rush Hour Counter → Book the last seat → 3 rounds (speed ×1.5 is fine) → "Verified" → booking card "Allowed by Cedar policy permit-motion-book" → DevPanel explain: "same token again → DENY forbid-token-replay" | "Three quick rounds and I'm verified. That gives me a single-use token that lives for two minutes. The booking goes through API Gateway, where a Lambda authorizer asks Cedar: allowed. Reuse the token and Cedar forbids it." |
| 1:02–1:45 | Lab: pick "Claude on Amazon Bedrock" (or Nova) → Let the AI try → progress → side by side "What the AI saw" (noise frames) vs "What you see" (animated) → wrong answers → **AI FAILED** → scoreboard with CIs | "Now the red team. A Strands agent on Amazon Bedrock gets the same puzzle, told exactly how it works, with four consecutive frames. It guesses. Across our runs: humans pass X percent; the best model, Y, at chance. Numbers with confidence intervals are in the repo." |
| 1:45–2:15 | Quick AWS console cuts (3–4 s each): Amplify app · API Gateway routes + 2 authorizers · Lambda functions list · CloudWatch Logs Insights `authz_decision` rows · DynamoDB `STATS#mdg-v1` items · Cognito user pool · Secrets Manager (name only) · Bedrock model in use | "It's all serverless on AWS: Amplify hosts the app; API Gateway and Lambda run the challenge and the Cedar authorizer; DynamoDB keeps single-use state and stats; Secrets Manager holds the signing key; Bedrock powers the red team. A verification costs a fraction of a cent; the whole weekend cost $Z." |
| 2:15–2:35 | Terminal: `make local-up` · `make local-api` · `make cedar-demo` (table) · `make bench BACKEND=ollama …` → summary "0/5" | "And it runs on my laptop: SAM CLI emulates the API and the Cedar authorizer, DynamoDB Local stores state, and a local vision model via Ollama and Strands fails the same way." |
| 2:35–2:48 | `/account`: Cognito sign-in → token assurance=account → booking "1/2 today" | "Motion puzzles aren't for everyone, so there's a non-puzzle path: a verified account through Cognito, with a daily quota enforced by the same Cedar policies." |
| 2:48–2:58 | About page limitations box, then repo URL | "It isn't unbreakable: a custom optical-flow solver can crack it. But it forces attackers back to building a solver per puzzle, instead of just pointing an agent at it. Code's in the description." |
Replace X/Y/Z with numbers **from `eval/report.md` and the Billing console**, never estimates.

## 2. Recording checklist
- [ ] 1920×1080, browser zoom 110–125%, bookmarks bar hidden, notifications off, clean profile, dark UI.
- [ ] Warm up: run one challenge + one booking + one Lab run just before recording (avoid cold starts on camera).
- [ ] Have a finished Lab run open in a second tab in case Bedrock is slow; you can cut to it.
- [ ] AWS console tabs pre-opened in the order of the script; region us-east-1; hide the account id (crop) and emails.
- [ ] Terminal: large font (18–20 pt), clear screen, commands typed or pasted, output visible.
- [ ] Record segments separately (OBS / QuickTime / Windows Game Bar); edit in CapCut / DaVinci Resolve / iMovie.
- [ ] Voiceover recorded separately in a quiet room; captions burned in or uploaded (auto-captions + fix names).
- [ ] Final length ≤ 2:58. Export 1080p. Watch it once end-to-end with sound off: does the story still read?

## 3. Upload
YouTube → visibility **Public** or **Unlisted** (never Private) → title "PACT: human verification AI agents can't
fake (WeMakeDevs × AWS First Commit)" → description: one-paragraph summary, repo link, live URL, AWS services,
"#BharatBuilds". Check the link in a logged-out/incognito window. Paste the link into the writeup and README.
