# DEMO VIDEO — ≤ 3:00 on YouTube (target 2:52). "If the video doesn't show it, it doesn't count."

Flow: screen puzzles keep getting harder → our motion puzzle (humans pass, the Bedrock agent fails) → but AI keeps
improving → physical verification on a phone → AWS under the hood → the honest limit (sensor forgery) → the
vendor-attested future. **S** = Satvik, **T** = teammate ([Name]). Public name: **ARHV**.
Motion-graphic clips (silent, 1080p/30, made with HyperFrames): `seg02_clip1_solved_by_ai.mp4` (10 s),
`seg06_clip2_moving_target.mp4` (12 s), `seg09_clip4_on_aws.mp4` (14 s), `seg11_clip3_vendor_future.mp4` (16 s),
`seg12_clip5_end_card.mp4` (5 s). Beat 9 is mandatory: the rules require AWS to be *visibly shown*.

## 1. Script
| # | Time | Where | Who | Lines |
|---|---|---|---|---|
| 1 | 0:00–0:12 | Screen: real CAPTCHAs, ~2 s cuts: distorted text → "I'm not a robot" → image grid → a harder puzzle → **AWS WAF CAPTCHA puzzle** (Google's reCAPTCHA demo page; AWS docs "CAPTCHA puzzle examples") | T (VO) | "For twenty years we've proved we're human by solving puzzles. And they keep getting harder — for us." |
| 2 | 0:12–0:22 | Clip 1 "Solved by AI" | T (VO) | "Because AI keeps solving them. Vision models clear image CAPTCHAs, and AI agents now click 'I'm not a robot' on their own." |
| 3 | 0:22–0:32 | **Face cam, both** | S, T | S: "I'm Satvik—" T: "—and I'm [Name]." S: "We asked: what's effortless for people but invisible to an AI that sees the web through screenshots? Motion." |
| 4 | 0:32–0:54 | Laptop browser, **Amplify URL visible**: ARHV Rail counter → Search trains → Book this journey → Quick presence check → the motion puzzle → *(editor: freeze one frame, label "what an AI's screenshot sees")* → 3 picks → verified → "Allowed by Cedar policy `permit-motion-book`" | S (VO) | "There's a shape hidden in these dots. The dots inside it move together, so you see it instantly. Freeze any single frame and it's pure noise — and a frame is all a screenshot-driven agent gets. Three rounds, verified, booked." |
| 5 | 0:54–1:12 | Terminal: `make bench …` run → `eval/report.md` table | T (VO) | "Now the red team. An AI agent built with Strands on Amazon Bedrock gets the same puzzle, knows exactly how it works, and sees four consecutive frames. Across twenty puzzles it solved zero, and its rounds were no better than guessing." Source: `eval/report.md`, Nova 2 Lite, K=4: 0/20 puzzles, 12/60 rounds (95% CI 0.118–0.318; chance 0.167). Add "Our testers: Y of N" only with real `/v1/stats` pilot counts. |
| 6 | 1:12–1:24 | Clip 2 "Moving target" | S (VO) | "But that's a snapshot of today's AI. Any puzzle on a screen is a speed bump, and every new model clears a higher one." |
| 7 | 1:24–1:32 | **Face cam, [Name]** | T | "So we stopped asking what you can *see* — and started asking what you can *physically do*." |
| 8 | 1:32–1:57 | **Phone, split screen:** phone screen recording (URL bar visible) + camera on the hands tilting. Book this journey → Quick presence check → Tilt your phone gently → Start physical check → Allow → dot fills 3 rings → "Presence verified · physical proof" → "Allowed by Cedar policy `permit-physical-book`" | S (VO) | "Tilt the phone and roll the dot through three rings the server just picked at random. The phone streams its accelerometer, gyroscope and orientation, and the server checks the physics: does gravity match the tilt, does the gyroscope match the motion, were the targets hit in order? Verified — booked." |
| 9 | 1:57–2:11 | Clip 4 "On AWS", then 2–3 s console cuts: API Gateway routes · CloudWatch `authz_decision … permit-physical-book` · DynamoDB items | T (VO) | "All serverless on AWS: Amplify hosts it, API Gateway and Lambda run the checks, Cedar policies decide every booking, DynamoDB makes each token single-use, and Bedrock powers the red team." |
| 10 | 2:11–2:28 | Terminal: `make imu-demo IMU_API=<api>` → 5 REJECTED, highlight the last row PASSED | S (VO) | "The honest part: sensor data can be faked. Emulated sensors, a phone flat on a desk, replayed recordings — all rejected. But a physics-perfect simulator passes. That's not an AI solving a puzzle anymore; it's a deliberate attack forging sensor data." |
| 11 | 2:28–2:44 | Clip 3 "Vendor-attested future" | T (VO) | "And hardware can sign its own signals. Windows 11 made TPM chips mandatory. Let phones and laptops attest a fresh physical gesture — a tilt, a hinge, a fingerprint touch — privately, with no identity attached. That's the future of human verification." |
| 12 | 2:44–2:52 | **Face cam, both** → Clip 5 end card | S, T | S: "Agents can read any screen." T: "They can't tilt your phone." S: "ARHV. Code's in the description." |

## 2. Recording order and checklist
1. Face cams (beats 3, 7, 12): landscape, eye level, window light, 2–3 takes each.
2. Phone demo (beat 8): phone screen recording and a second camera on the hands at the same time; Do Not
   Disturb, portrait lock, brightness up; practise the tilt twice first.
3. Laptop screen recordings: CAPTCHA pages, motion puzzle, `make bench`, `make imu-demo`, AWS console
   (us-east-1; crop the account id and any email). Warm up the API with one booking first.
4. Voiceover in one sitting, one take per beat. Then lay out beats 1–12, drop the clips in, fit clips to the
   voiceover (speed 0.9–1.1× or trim the holds). Final length ≤ 2:58; watch once with sound off.
Numbers in beat 5 come only from `eval/report.md` / `/v1/stats` (the agent result above is the recorded local run). Never present emulation or the simulator as a
real phone. Credit HyperFrames in the README if the clips are used.

## 3. Upload
YouTube → **Public** or **Unlisted** → title "ARHV: human verification AI agents can't fake, with physical proof
on AWS (WeMakeDevs × AWS First Commit)" → description: 3-line summary, repo link, live URL, AWS services,
"#BharatBuilds". Check it plays logged-out; paste the link into the writeup and README.
