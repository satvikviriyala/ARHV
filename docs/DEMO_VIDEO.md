# DEMO VIDEO — ≤ 3:00 on YouTube (aim for 2:50). "If the video doesn't show it, it doesn't count."

Story in one line: **screen puzzles are a race agents win → physical proof works today (live) → here's exactly
where the web falls short (live attack table) → vendors can close it (the TPM moment) → all of it on AWS.**
Public name on screen and in the voiceover: **ARHV**.

## 1. Script (voiceover + what's on screen). Every AWS service named must be *visible* when named.
| Time | On screen | Voiceover (tight; calm pace) |
|---|---|---|
| 0:00–0:15 | Text overlays with sources: "Vision models solve 100% of reCAPTCHAv2 image challenges (ETH Zürich, 2024)" · "AI agents click 'I'm not a robot' (2025)" · "Tatkal: bot traffic peaks in the first minutes" → title card **ARHV · Agent-Resistant Human Verification** | "Every CAPTCHA on a screen is a puzzle, and AI agents are getting better at puzzles than we are. So scarce slots, like Tatkal tickets, go to bots in minutes. We asked a different question: what can a person do that a screen-only agent can't?" |
| 0:15–0:50 | Split screen: **phone screen recording with the Amplify URL visible** + a camera shot of a hand tilting the phone. Rush Hour Counter → Book the last seat → **Tilt your phone** → Start physical check → (iOS: Allow) → dot rolls into 3 rings, each fills → "Verified · physical proof" → booking card "Allowed by Cedar policy `permit-physical-book`" | "Tilt the phone and roll the dot into three rings the server just picked at random. The phone streams its accelerometer, gyroscope and orientation, and the server checks the physics: does gravity agree with the tilt, does the gyroscope agree with the motion, were the targets hit in order? Pass, and I get a single-use, two-minute token. API Gateway's Lambda authorizer asks Cedar: allowed." |
| 0:50–1:15 | Terminal (big font): `make imu-demo IMU_API=https://…execute-api…` against the **live API**: 5 rows REJECTED with reasons, then the last row **PASSED** highlighted | "Now let's attack it. Sensor emulation, like DevTools: rejected, there's no real gravity. A dead gyroscope: rejected. A phone lying flat on a desk: rejected. A teleporting bot: rejected. A replayed real recording: rejected, the targets changed. But a physics-perfect simulator passes. We show that on purpose: a web page can't prove its sensors are real." |
| 1:15–1:40 | Graphic: three tiers (Perceptual · Physical · Vendor-attested) → code card `navigator.physical.request({gesture, challenge})` → overlay "Windows 11 made TPM 2.0 mandatory" → icons: phone tilt, laptop hinge, fingerprint | "That gap is for device makers to close, the way Windows 11 made TPM 2.0 mandatory. Let the operating system run the gesture in a trusted overlay, let the secure sensor hub and enclave sign 'a real device felt this fresh gesture', and give the site a private, unlinkable token. Tilt a phone, open a laptop hinge, touch a fingerprint sensor: physical, attested, private." |
| 1:40–2:05 | Laptop, **Amplify URL visible**: "Spot the shape" motion puzzle → 3 rounds → Verified. Cut to terminal: `make bench BACKEND=bedrock MODEL=nova-2-lite …` summary + `eval/report.md` table with CIs | "No phone? The perceptual tier hides a shape in moving dots. You see it instantly; a screenshot sees noise. Our Strands agent on Amazon Bedrock, given four frames, got X of N; our human testers got Y of N. Today's agents fail, but that's a moving target, and physical proof is how we step off the treadmill." |
| 2:05–2:40 | AWS console cuts (3–4 s each): Amplify app · API Gateway routes + authorizers · Lambda functions · DynamoDB items (`STATS#imu-v1`, `JTI#…`) · CloudWatch Logs Insights `authz_decision` rows (ALLOW `permit-physical-book`, DENY `forbid-token-replay`) · Secrets Manager (name only) · Bedrock model | "All of it is serverless on AWS. Amplify hosts the app; API Gateway and Lambda run both verifiers and the Cedar authorizer; DynamoDB makes every challenge and token single-use; Secrets Manager holds the signing key; Bedrock powers the red team. Replay the token and Cedar forbids it. A verification costs a fraction of a cent." |
| 2:40–2:55 | `make cedar-demo` table → README limitations box → repo URL | "The policies are open-source Cedar, testable offline. Honest limits: web sensors are unattested, and a human farm can still tilt phones; quotas handle that. Agents can think. They can't tilt. The code is in the description." |
Replace the agent sentence with the observed local result from `eval/report.md`: Nova 2 Lite, K=4, 0/20
full puzzles and 12/60 rounds correct (95% CI [0.1183, 0.3178]). Add human counts only after H16 produces
real `/v1/stats` data; if the live Bedrock/human runs did not happen, cut those sentences rather than guess.

## 2. Recording checklist
- [ ] Phone: Do Not Disturb, brightness up, portrait lock on, Safari/Chrome with the Amplify URL bar visible.
      iPhone: Control Center → Screen Recording (enable in Settings → Control Center first). Android: Quick
      Settings → Screen record. Practise the tilt twice first so the take is smooth.
- [ ] Second camera (a friend's phone) films the hand tilting the phone: this shot *is* the thesis.
- [ ] Laptop: 1920×1080, browser zoom 110–125%, bookmarks bar hidden, notifications off, dark UI.
- [ ] Warm up the API (one challenge + one booking) right before recording to avoid cold starts on camera.
- [ ] Terminal: 18–20 pt font, cleared, commands pasted, output visible; crop the AWS account id and any email.
- [ ] Record segments separately; edit in CapCut / iMovie / DaVinci Resolve; voiceover recorded separately.
- [ ] Captions (auto + fix "ARHV", "Cedar", "Bedrock"). Final length ≤ 2:58. Watch once with sound off.

## 3. Upload
YouTube → **Public** or **Unlisted** (never Private) → title "ARHV: human verification AI agents can't fake,
with physical proof on AWS (WeMakeDevs × AWS First Commit)" → description: 3-line summary (thesis, what's live,
the vendor proposal), repo link, live URL, AWS services, "#BharatBuilds". Check the link logged-out. Paste the
link into the writeup and README.
