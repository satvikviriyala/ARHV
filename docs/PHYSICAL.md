# PHYSICAL — why the future of human verification is physical, and what ARHV builds today

> **Thesis.** Any human-verification test that lives entirely in the digital channel (text, images, puzzles,
> even our motion-defined glyphs) is a capability race, and agents win capability races. The durable boundary
> is physical: *prove that a human just moved a real device, for this request*. Today's browsers can only give
> us **unattested** sensor streams, which a determined attacker can synthesise. So the endgame needs **vendor
> support**: OS/hardware makers attesting a physical gesture, the way Windows 11 made TPM 2.0 mandatory so
> disk encryption and credentials could rest on hardware. ARHV ships the working prototype and the protocol.

## 1. The argument in four steps (use this order in README, video and writeup)
1. **Digital-only tests are a moving target.** Image CAPTCHAs fell to vision models (100% of reCAPTCHAv2
   image challenges solved, 2024); agents click "I'm not a robot" (2025); reasoning models reach up to 90% on
   complex logic puzzles (2026). ARHV's own motion-defined glyph (mdg-v1) defeats *screenshot* agents today, but
   a purpose-built optical-flow solver beats it, and future video-native agents may too. Every non-physical test
   is a speed bump whose height is set by today's models.
2. **Physical interaction is a different kind of evidence.** An agent can read a screen and drive a browser;
   it cannot tilt a phone in your hand. A fresh, server-randomised physical gesture turns "can you *perceive*
   X" into "did a person *physically do* X, just now, for this request".
3. **But the web can't prove the sensors are real.** Browser motion APIs (DeviceOrientation/DeviceMotion) are
   unattested: DevTools can emulate them and automation can inject streams. ARHV's verifier demonstrates both
   halves honestly: it rejects every cheap spoof (orientation-only, dead gyro, desk-flat gravity, teleporting,
   replayed recordings) using cross-sensor physics, **and** a physics-consistent simulator still passes
   (`scripts/imu_attack_demo.py`, `test_physically_consistent_synthetic_trace_passes_documenting_the_attestation_gap`).
4. **So vendors must attest physical gestures, as TPM did for encryption.** The pieces already exist: secure
   sensor hubs, Secure Enclave/TPM/StrongBox keys, Apple Private Access Tokens (device attestation replacing
   CAPTCHAs since iOS 16), Play Integrity and App Attest (nonce-bound app/device integrity), WebAuthn user
   presence (Touch ID, Windows Hello), and **Private Access Control Tokens (PACT)**, announced on June 22, 2026 by
   Cloudflare with Chrome, Firefox, Edge and Shopify: anonymous tokens that prove "a human is in the loop",
   issued today by sites that already have an authentic relationship with the person. What's missing is one
   primitive: **"a real device experienced this randomised physical gesture, for this nonce"**, exposed to the web
   in a privacy-preserving, open way (§7). Google's Web Environment Integrity was withdrawn in 2023 after
   criticism over openness and privacy; the physical-proof primitive must learn from that (§7.3).

## 2. Assurance tiers (ARHV's proof families)
| Tier | Proof family | Status | Beats | Loses to |
|---|---|---|---|---|
| T0 perceptual | `mdg-v1` motion-defined glyph | built (Phases 1–2) | screenshot/VLM agents, cheap scripts | purpose-built optical-flow solvers; future video agents |
| T1 physical, unattested | `imu-v1` phone-tilt path, physics-verified | **built today (P1)** | orientation-only/flat/teleport/replay spoofs, all screen-only agents | physics-aware sensor simulators (demonstrated) |
| T2 physical, vendor-attested | `imu-attested` / `hinge-attested` / `presence-attested` | **proposal (§7)** + native prototypes later | all remote automation, simulators, emulators | a real human physically operating a real device (farms), handled by quotas/economics |
| Accessible alternatives | Cognito-verified account (+ WebAuthn UV roadmap) | account path documented | bulk bots (quota) | determined account farms |
Cedar decides which tiers an action needs (`permit-physical-book` today; tier requirements per resource in the roadmap).

## 3. `imu-v1` protocol (built today)
Reference implementation (tested): `backend/layers/core/pact_core/imu.py`, simulator/attacks
`redteam/imu_sim.py`, tests `backend/tests/test_imu.py` (21 tests, plus a 1,080-trace robustness sweep: iOS and
Android sign conventions × 30/60/100 Hz × three holding angles, all pass; ~5 ms per verification).
Frontend reference: `frontend/src/lib/imu.ts` (permission, capture, tracker) and `frontend/src/components/TiltChallenge.tsx`.

**Issue** (`POST /v1/challenges {"family": "imu-v1"}`): 3 targets, each a tilt offset of 16–26° in one of 8
directions (no immediate repeats) relative to the user's own baseline; radius 8°; hold 450 ms; baseline 600 ms;
30 s limit; fresh 128-bit nonce. Targets are **public by design** (they are the instructions); security comes from
freshness, timing and physics, not secrecy. Seeds come from `KeyedRng` (SHAKE-256), like mdg-v1.

**Capture** (phone browser, HTTPS only): after a tap, `DeviceMotionEvent.requestPermission()` **and**
`DeviceOrientationEvent.requestPermission()` (iOS 13+; Android Chrome streams without a prompt). One sample per
`devicemotion` event (~60 Hz), merged with the latest `deviceorientation`:
`[t_ms, beta, gamma, alpha|null, gx, gy, gz, rAlpha, rBeta, rGamma]` (≤ 4,000 samples, 0.1 precision, ~100 KB).
UI: "marble on a plate": tilt right → dot right; top toward you → dot down; fill each ring by holding inside it.

**Verify** (server re-derives everything; never trusts the client's "done"):
| Check | Rule | Stops |
|---|---|---|
| binding | trace echoes this `challengeId` + `nonce` | cross-challenge reuse |
| size/format | 30–4,000 samples of 10 finite numbers (alpha may be null) | malformed payloads |
| timing | monotonic; median interval 8–120 ms; max gap ≤ 750 ms; duration from baseline + holds to limit + 2 s | fast-forwarded or stitched traces |
| continuity | ≤ 30° between samples and ≤ 900°/s angular speed | teleporting scripted input |
| gravity | ≥ 80% of samples have ‖accelerationIncludingGravity‖ in 7.5–12.5 m/s² | orientation-only emulation (no real accelerometer) |
| tilt | on quasi-static samples, tilt implied by the gravity vector matches reported beta/gamma (median error ≤ 12°), trying both iOS and Android sign conventions | streams whose orientation and gravity come from different "worlds" |
| gyro | per moving axis, \|corr(d orientation/dt, rotationRate)\| ≥ 0.5 (scale- and sign-free) | dead or random gyroscope |
| targets | from the baseline median, each target held (≥ 80% of holdMs within radius + 2°) in order | replayed recordings (random targets differ), wrong paths |
Derivation used for the tilt check (W3C Z-X'-Y'' Euler, Android sign): `g_dev = (−g·cosβ·sinγ, g·sinβ, g·cosβ·cosγ)`,
so `β = atan2(gy, hypot(gx, gz))`, `γ = atan2(−gx, gz)`; iOS reports the opposite sign (handled).
Failure responses include `reasons` and `metrics` (Kerckhoffs: the rules are public). **We never store raw traces:**
keep only the metrics in logs/DynamoDB (privacy; motion data can fingerprint devices).

**Token:** pass → `asr: "physical"`, `prf: "imu-v1"`, 120 s, single-use `jti` → Cedar `permit-physical-book`.

**Tuning knobs (log changes):** if a real phone fails, read `metrics` and loosen only the failing rule
(e.g. `tiltErrDeg` limit 12 → 18 for devices with laggy sensor fusion; gyro corr 0.5 → 0.35; timing median up to
200 ms for low-rate devices). Never loosen binding, targets or continuity.

## 4. Laptop → phone handoff (stretch P2; routes already in the template)
The phone is the physical verifier for any computer: the laptop shows a QR; the phone completes `imu-v1`; the
laptop receives the token. `POST /v1/handoffs` → `{handoffId, pollKey, phoneKey, expiresAt}` (keys: 128-bit random;
store only SHA-256 hashes; TTL 5 min). The laptop shows a QR of `${location.origin}/phone?h=<handoffId>&k=<phoneKey>`.
Phone: `POST /v1/challenges {"family":"imu-v1","handoffId","phoneKey"}` → on pass the server mints the token into
the handoff record (`status: verified`) and tells the phone "Done, return to your computer". Laptop polls
`GET /v1/handoffs/{handoffId}` with header `x-pact-poll-key` every 1.5 s → receives the token **once**
(`status → delivered`). Neither key alone lets a third party both verify and collect.

## 5. Threat model for physical proofs
| Attacker | T1 web `imu-v1` | T2 vendor-attested |
|---|---|---|
| Screenshot/computer-use agent (no device) | fails: no sensor stream | fails |
| DevTools/automation orientation emulation | fails: gravity/tilt/gyro inconsistent (demo) | fails: no attestation |
| Replay of a genuine recording | fails: fresh random targets + nonce (demo) | fails: nonce in the signed statement |
| Physics-aware simulator (synthetic IMU) | **passes** (demo; this is the attestation gap) | fails: sensor hub signs only real readings |
| Rooted/emulated device feeding the attested API | n/a | hard: attestation keys + integrity verdicts (Play Integrity/App Attest style) |
| Human farm physically tilting phones | passes | passes; mitigated by Cedar quotas, rate limits, cost |
| Motor-impaired user | may fail | may fail; offer account/WebAuthn paths (accessibility) |

## 6. Other physical channels (roadmap, not built this weekend)
- **Laptop hinge (`hinge-v1`).** MacBooks from the 2019 16-inch Pro onward have a lid-angle sensor, but not the
  M1/M2 generation, and there is **no public API**; community tools read it through undocumented HID access. A
  randomised "open to ~105°, then ~80°" gesture would be a delightful laptop proof, and it is the clearest example
  of why vendor support is needed: only Apple can expose it, attest it, and make it universal.
- **Fingerprint/touch presence.** Touch ID and Windows Hello already attest *user presence/verification* through
  WebAuthn (TPM-backed on Windows). ARHV's roadmap uses WebAuthn with `userVerification: "required"` as a
  presence proof (assurance `presence`) with no identity disclosure beyond an ephemeral credential.
- **Phone as universal verifier** (§4) covers desktops, Chromebooks, kiosks and Linux today.
- **Not pursued:** camera/microphone liveness (privacy), behavioural biometrics as a decision (brittle, excludes
  disabled users; at most a risk signal).

## 7. Proposal: vendor-attested physical gestures (the TPM moment for human verification)
### 7.1 Primitive
`navigator.physical.request({gesture: "tilt-path" | "lid-angle" | "presence-touch", challenge: <server nonce +
signed gesture spec>})`. The **OS**, not the page, renders the gesture UI in a trusted overlay (like the Touch ID
or passkey sheet), so a page or agent can't drive or fake it. The secure sensor hub (or TEE) evaluates the gesture
against the spec and the Secure Enclave/TPM/StrongBox signs `{origin, nonce, gestureSpecHash, result, time}`.
### 7.2 Output
Not a device identity. The browser redeems the attestation for a **Privacy Pass / anonymous-credential token**
(as Apple Private Access Tokens already do for device attestation). The natural carrier is **Private Access Control
Tokens (PACT)**: today those tokens are issued by sites that have an authentic relationship with the person (an
account); a vendor-attested fresh physical gesture is an issuance signal that needs **no identity at all**, so
people without such accounts are not left out. The site learns "a real device observed this fresh physical
gesture", nothing else.
### 7.3 Principles (learning from Web Environment Integrity's withdrawal)
Open W3C/IETF standard; any browser can implement; unlinkable tokens; no device fingerprinting; always an
accessible non-gesture alternative; sites can't block browsers/OSes that don't implement it (fallbacks: T0/T1 +
quotas); attestation roots published.
### 7.4 How ARHV plugs in
The token's `asr` becomes `physical-attested`; Cedar policies require it only for high-risk actions
(e.g. `forbid ... when resource.kind == "high_demand" && principal.assurance == "motion"` in a strict profile).
Native prototypes that are possible *today* without new OS APIs: an Android app binding the IMU trace hash to a
Play Integrity `requestHash`, and an iOS app signing it with App Attest; both on the roadmap.

## 8. Prior art and positioning (cite it; it makes the claim stronger)
SenCAPTCHA (IMWUT 2020) proposed a mobile tilt-to-target CAPTCHA using orientation sensors. Anti-bot vendors use
motion streams as risk signals and note that realistic streams can be replayed or synthesised. ARHV's contribution:
(1) the thesis that digital-only tests are a losing race, backed by our own red team on both families;
(2) server-side cross-sensor physics verification with fresh randomised paths; (3) proof tiers expressed as
Cedar authorization policy on AWS; (4) a concrete, privacy-first vendor-attestation primitive that closes the gap
we measured.

## 9. Sources
- Windows 11 requires TPM 2.0: https://learn.microsoft.com/en-us/windows/whats-new/windows-11-requirements
- Apple Private Access Tokens (WWDC22): https://developer.apple.com/videos/play/wwdc2022/10077/ · Cloudflare Privacy Pass: https://blog.cloudflare.com/privacy-pass-standard/
- Private Access Control Tokens (PACT), Cloudflare with Chrome, Firefox, Edge and Shopify (June 22, 2026): https://www.cloudflare.com/press/press-releases/2026/cloudflare-collaborates-with-leading-browsers-to-develop-a-privacy-first-protocol-for-the-global-internet/ · Mozilla Hacks, "PACT: Anonymous Credentials for the Web": https://hacks.mozilla.org/2026/06/pact-anonymous-credentials-for-the-web/
- Google abandons Web Environment Integrity (Nov 2023): https://www.theregister.com/software/2023/11/02/google-abandons-web-environment-integrity-api-proposal/335969
- Play Integrity standard requests (requestHash): https://developer.android.com/google/play/integrity/standard · App Attest: https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity
- SenCAPTCHA: https://dl.acm.org/doi/10.1145/3397312 · Motion signals in bot detection: https://blog.crawlex.net/blog/device-orientation-accelerometer-bot-detection/
- W3C Device Orientation and Motion: https://www.w3.org/TR/orientation-event/ · web.dev guide: https://web.dev/articles/device-orientation
- MacBook lid-angle sensor (community, undocumented): https://github.com/samhenrigold/LidAngleSensor
- Agents vs CAPTCHAs: https://arxiv.org/abs/2409.08831 · https://arxiv.org/abs/2602.09012
