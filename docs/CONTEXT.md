# CONTEXT — the hackathon, the judging, and the real problem

## 1. Event facts (verified Sept 19, 2026 from the official pages)
- **Event:** WeMakeDevs × AWS "First Commit" (Bharat Builds Tour). Online across India, **Thu–Sun, Sept 17–20, 2026**;
  optional in-person day Sat Sept 19 (Bangalore). Venue and online entries are judged by the same panel.
- **Eligibility:** university students in India, 18+. Teams of 1–4, each member registered individually.
  WeMakeDevs account + **AWS Builder Center profile with student verification** required.
- **Deadline:** the schedule page said "hours are being finalised" when this was written. **Confirm the exact
  cut-off** at https://www.wemakedevs.org/aws/first-commit/schedule (or the Discord/email) and write it into
  `MEMORY.md › Snapshot`. The plan assumes Sun 20 Sept 23:59 IST and submits early at M2 regardless.
- **Submission = 3 things:** public repository + demo video **uploaded to YouTube, under three minutes** + short
  writeup covering **the problem, the build, and where AWS fits**. Submit on the hackathon's own form, once per
  team; editable until the deadline, then locked.
- **Rules that shape the build (quoted):**
  - "Start building when the hackathon opens … Old projects do not count … even if you rewrote it."
  - "You can use open-source libraries, frameworks, public APIs, boilerplate and starter templates. What gets
    judged is what you added during the event."
  - "Your project has to use AWS, and your demo video has to show it. Naming AWS in the writeup alone is not enough."
  - "You can use AI coding tools. List the ones you used in your writeup."
  - "Anything you did not write needs a credit and a licence that allows you to use it."
  - "Judges score what you submit and nothing else. There is no live demo and no call. If the video does not show
    it, it does not count, and a feature that exists only in the writeup does not count either."

## 2. Tracks and prizes (one submission is considered for all three; nothing to pick)
| Prize | Reward | What decides it |
|---|---|---|
| **Ship It** (first) | ₹2,00,000 + $3,000 AWS credits | Deployed with a URL: Lambda, API Gateway, DynamoDB, S3, Bedrock, Amplify, Cognito… "architecture and cost decisions are part of the score" |
| **Build It** (second) | ₹1,50,000 + $2,000 credits | Open source on your machine: Strands Agents, Cedar, SAM CLI + LocalStack, PartyRock, OpenSearch… |
| **Best UI** (third) | ₹1,00,000 + $1,000 credits | The interface |
| Runners-up ×4 | $1,000 credits each | |
| **Top 5 blogs** | Logitech gaming keyboard each | Blog published on **AWS Builder Center**, linked in the submission |
| Top 10 students | Fast-track Amazon interview (internship + full-time) | From top projects |

## 3. Judging criteria (the page lists five; no weights published)
1. **Idea and Impact:** "Does it solve a real problem? And what changes for the people on the other side of it?
   A small problem solved well beats a big one solved vaguely."
2. **Built on AWS:** "Using an AWS open-source project or AWS services is mandatory to win a prize." Grand prize is
   decided in Ship It, where architecture and cost count.
3. **Learning:** "Four days should leave you knowing something you didn't on Thursday." Write it down.
4. **The execution:** "Does it work? Not perfect, not polished. Working." One feature that runs beats five that
   almost do.
5. **The demo video:** "Three minutes, recorded, to show what it does, who it is for, and where AWS fits."

## 4. Credits and accounts
- A new AWS account comes with up to **$200 in credits** (valid for every track). Teams can request an **extra
  $100** via the hackathon's Google form. Bedrock has no permanent free tier, so credits cover it; keep a budget alarm.
- Amazon Bedrock now enables serverless models **by default** in commercial regions; **Anthropic models still
  need a one-time use-case form** before first use.
- LocalStack **Community edition ended on March 23, 2026**: the image now needs a (free for non-commercial and
  student) account and `LOCALSTACK_AUTH_TOKEN`. That's why our local default is **DynamoDB Local** (no account).

## 5. The real problem (use these facts in README, About page, writeup and video; all are cited)
**Who is on the other side:** the student trying to book a Tatkal ticket home, the family refreshing for a scarce
slot, the fan against scalper bots. Any first-come-first-served public slot where the bots win in the first minutes.

1. **CAPTCHAs are India's front-line bot filter, and bots still win the first minutes.**
   - Indian Railways deactivated **2.5 crore** suspected user IDs by June 2025. Bot traffic "peaks during the first
     five minutes of Tatkal", and Railways deployed anti-bot systems and a CDN to fight it (AIR, June 4, 2025).
   - Aadhaar-based OTP authentication was made **mandatory for online Tatkal bookings from July 15, 2025**
     (AIR, June 11, 2025). Identity friction was added for *everyone* because bot filtering wasn't enough.
   - **3.03 crore** suspicious IRCTC user IDs were deactivated in 2025, with "a CAPTCHA mechanism deployed at
     multiple levels to avoid scripting" (Railways Minister's written reply in the Rajya Sabha, AIR, Feb 13, 2026).
2. **AI agents now beat CAPTCHAs.**
   - ETH Zurich solved **100%** of reCAPTCHAv2 image challenges with YOLO models (Plesner et al., arXiv:2409.08831, 2024).
   - OpenAI's ChatGPT Agent clicked Cloudflare's "verify you are human" box while narrating it (widely reported, July 2025).
   - Reasoning models such as Gemini 3 Pro-High and GPT-5.2-XHigh reach **up to 90%** on complex CAPTCHA logic puzzles
     like "Bingo" ("Next-Gen CAPTCHAs", arXiv:2602.09012, 2026). Its authors argue for exploiting the human–agent
     "cognitive gap" in interactive perception, which is exactly PACT's approach.
   - Open CaptchaWorld (arXiv:2505.24878, 2025): humans 93.3% vs best agent (Browser-Use o3) 40%. Even then, the
     gap was already closing.
3. **CAPTCHAs also fail people.** W3C's note "Inaccessibility of CAPTCHA" documents how visual/audio CAPTCHAs exclude
   disabled users; WCAG 2.2 **SC 3.3.8 Accessible Authentication (Minimum)** requires an alternative to cognitive
   function tests. PACT ships a non-cognitive account path for exactly this reason.

4. **Why the answer has to become physical (ARHV's thesis; full argument in `docs/PHYSICAL.md`).**
   - Every digital-only test is a capability race: the items above show image, checkbox and logic CAPTCHAs falling
     in turn, and each new puzzle is set by today's model limits.
   - The platform precedent exists: **Windows 11 requires TPM 2.0**, so disk encryption and credentials rest on
     hardware; **Apple Private Access Tokens** (iOS 16, 2022) already replace some CAPTCHAs with device attestation;
     **Play Integrity** and **App Attest** bind nonces to genuine devices/apps; **WebAuthn** already attests user
     presence (Touch ID, Windows Hello).
   - What's missing is one primitive: "a real device experienced this fresh, randomised physical gesture", open and
     privacy-preserving. **Google's Web Environment Integrity** proposal was withdrawn (Nov 2023) after openness
     and privacy criticism, which gives the design rules. **Private Access Control Tokens (PACT)**, announced June 22,
     2026 by Cloudflare with Chrome, Firefox, Edge and Shopify, show where the industry is going: anonymous
     "human in the loop" tokens instead of CAPTCHAs, issued by sites with authentic user relationships. ARHV's
     proposal adds an issuance signal that needs no identity: a vendor-attested physical gesture.
   - Prior art for phone-tilt CAPTCHAs: **SenCAPTCHA** (IMWUT 2020). ARHV's contribution is the cross-sensor
     physics verifier, the measured attestation gap, Cedar-expressed proof tiers on AWS and the vendor proposal.

**ARHV's claim (keep it this precise):** (1) the physical tier (`imu-v1`) proves more than any screen puzzle can:
screen-only agents have no sensor stream, and cheap sensor spoofs fail server-side physics checks; but web sensors
are unattested, so a physics-aware simulator passes (shown). (2) The perceptual tier (`mdg-v1`) is described next.
(3) Closing the gap requires vendor attestation, which we specify.

**The perceptual tier's claim (keep it this precise):** a human-verification step whose answer is carried only by motion. Any
single frame is noise, so screenshot-driven agents (today's cheap, general-purpose automation) are reduced to
guessing, while humans pass in seconds. It is **not** unbreakable: a bespoke optical-flow solver written for this
specific puzzle can beat it (see `docs/SECURITY.md`). PACT moves attackers from "point any agent at it" back to
"engineer a custom solver per puzzle family", which is the cost asymmetry CAPTCHAs relied on before general agents.

## 6. Why ARHV scores on every criterion
- **Impact:** concrete Indian problem (Tatkal and scarce slots) + a global one (agents vs CAPTCHAs) + accessibility.
- **AWS:** eight managed services on the critical path, visible in the video; clear cost story (pennies per 1,000
  verifications; the red team costs cents).
- **Learning:** perception science, Cedar ABAC, Strands agents, SAM, honest red-teaming.
- **Execution:** one sharp loop that works (verify → token → Cedar → action) and a measurable result.
- **Video:** a real hand tilting a real phone, then the live spoof table with the honest "simulator passes" row,
  then "what the AI saw vs what you see". The thesis is visible, not asserted.
- **Idea:** a position, not just a puzzle: human verification must become physical and vendor-attested, with a
  concrete, privacy-first primitive (docs/PHYSICAL.md §7).

## 7. Sources
- Hackathon: https://www.wemakedevs.org/aws/first-commit · rules: https://www.wemakedevs.org/aws/first-commit/rules · schedule: https://www.wemakedevs.org/aws/first-commit/schedule
- AIR, June 4, 2025 (2.5 crore IDs; bot traffic in the first five minutes of Tatkal): https://www.newsonair.gov.in/railways-deactivate-more-than-2cr-unauthorised-booking-ids
- AIR, June 11, 2025 (Aadhaar OTP mandatory from July 15, 2025): https://www.newsonair.gov.in/aadhaar-authentication-made-mandatory-for-online-tatkal-ticket-booking-from-july-15
- AIR, Feb 13, 2026 (3.03 crore IDs; multi-level CAPTCHA): https://www.newsonair.gov.in/over-3-crore-suspicious-user-ids-deactivated-using-aadhaar-cybersecurity-railways-minister-ashwini-vaishnaw/
- Breaking reCAPTCHAv2 (ETH Zurich): https://arxiv.org/abs/2409.08831
- ChatGPT Agent vs "I am not a robot": https://www.tomshardware.com/tech-industry/artificial-intelligence/chatgpt-agent-casually-brushes-aside-i-am-not-a-robot-captcha-so-now-ill-click-the-verify-you-are-human-checkbox-to-complete-this-verification-it-declared-without-a-hint-of-irony
- Next-Gen CAPTCHAs (2026): https://arxiv.org/abs/2602.09012
- Open CaptchaWorld (2025): https://arxiv.org/abs/2505.24878
- W3C, Inaccessibility of CAPTCHA: https://www.w3.org/TR/turingtest/ · WCAG 2.2 SC 3.3.8: https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum
- Bedrock automatic model enablement: https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-automatic-enablement-serverless-foundation-models
- LocalStack 2026 changes: https://blog.localstack.cloud/2026-upcoming-pricing-changes/
- Physical-proof sources (TPM 2.0, Private Access Tokens, Play Integrity, App Attest, WEI, Private Access Control Tokens,
  SenCAPTCHA, W3C Device Orientation): `docs/PHYSICAL.md §9`
