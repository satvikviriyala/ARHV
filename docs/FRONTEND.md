# FRONTEND — React app on Amplify Hosting (also the "Best UI" entry)

Verified toolchain (scaffold `docs/reference/scaffold/frontend`, lockfile included): **Vite 8, React 19.3,
TypeScript 6, Tailwind CSS 4 (`@tailwindcss/vite`), React Router 8 (`react-router`), aws-amplify 6 +
@aws-amplify/ui-react 6, lucide-react, Vitest 5 + jsdom, ESLint 10 flat config.** `npm run build`, `npm run lint` and
`npx vitest run` pass on the scaffold. Use `npm ci` (lockfile) unless adding a dependency.
Peer-range note: npm flags a nested `@xstate/react` peer range (React ≤ 18) inside Amplify UI. It installs and builds
fine. If a future `npm install` errors with ERESOLVE, use `npm install --legacy-peer-deps` and log it.

## 1. Routes and pages (React Router 8: `createBrowserRouter` + `RouterProvider` from `react-router`)
| Route | Page | Purpose |
|---|---|---|
| `/` | `Home` | Thesis hero + **ARHV Rail counter (fictional demo)**: search a journey → choose a service → **VerifyChooser** (phone tilt · motion puzzle) → booking card; scoreboard strip |
| `/phone` | `Phone` | Mobile-first physical check (`imu-v1`) → booking card; handoff mode with `?h=&k=` (stretch) |
| `/lab` | `Lab` | Red-team lab: pick model + frames → run → "What the AI saw" → verdict; full scoreboard |
| `/about` | `About` | How it works, screenshot-vs-motion figure, architecture, Cedar policies, limitations, accessibility, credits, AI tools |
| `/account` | `AccountVerify` (**lazy**) | Cognito Authenticator → account token → back to booking (Phase 4) |
| `/booking/confirmed` | `BookingConfirmation` | Dedicated fictional ARHV Rail confirmation after the protected booking response |
Amplify SPA rewrite rule is set by `scripts/bootstrap_amplify.py` so deep links work.
`?cohort=study` on any URL → stored in `sessionStorage` and sent as `x-pact-cohort` on challenge creation.

## 2. File structure
```
frontend/src/
  main.tsx               RouterProvider; lazy() for /account (keeps Amplify UI + its CSS out of the main bundle)
  index.css              Tailwind import + @theme tokens (scaffold)
  config.ts              reads + validates VITE_* (throws a readable error screen if missing)
  lib/api.ts             typed client (all routes in docs/API.md), ApiError, 20 s timeout via AbortController
  lib/mdg.ts             decodeFrames, pingPongIndex (scaffold, tested)
  lib/imu.ts             requestMotionPermission, ImuRecorder, TargetTracker, types (exists, tested)
  lib/shapes.ts          GENERATED icons (scaffold; regenerate with `make shapes`)
  lib/cohort.ts          read ?cohort=, persist in sessionStorage, getCohort()
  lib/jwt.ts             decodePayload(token) for display only (no verification in the browser)
  lib/format.ts          pct(), ci(), ms()
  components/MdgCanvas.tsx        the player (§3)
  components/ShapeOptions.tsx     6 icon buttons, keys 1–6
  components/PactWidget.tsx       motion-puzzle state machine (§4); props: onVerified(token), cohort
  components/TiltChallenge.tsx    tilt UI, marble on a plate (exists; §13)
  components/PhysicalWidget.tsx   imu-v1 state machine (§13); props: onVerified(token), cohort, handoff?
  components/VerifyChooser.tsx    picks the proof (§13); QR to /phone on laptops
  components/BookingCard.tsx      counter UI + booking result
  components/DevPanel.tsx         token claims, Cedar explain, last API calls (collapsible)
  components/Scoreboard.tsx       humans vs agents with CIs + chance line
  components/AgentRunView.tsx     run progress, frames the AI saw, answers vs truth
  components/Layout.tsx, Header.tsx, Footer.tsx
  pages/Home.tsx, Phone.tsx, Lab.tsx, About.tsx, AccountVerify.tsx   (Lab/About/Account: cut list today)
  test/ (colocated *.test.ts[x] also fine)
```

## 3. `MdgCanvas` (the heart of the UI)
Props: `{ round: {frames: string; frameCount: number}; fps: number; dot: number; width: number; height: number;
autoplay: boolean; onFirstFrame?: () => void }`.
- `useMemo(() => decodeFrames(round.frames))` once per round.
- `<canvas width={160} height={160}>` styled `w-[min(88vw,420px)] aspect-square [image-rendering:pixelated] rounded-2xl`.
- `requestAnimationFrame` loop: `tick = floor((now - t0) * fps / 1000)`, `i = pingPongIndex(tick, frameCount)`; draw
  only when `i` changes: `fillStyle = bg; fillRect(0,0,160,160); fillStyle = dot color; for each (x,y) fillRect(x,y,dot,dot)`.
- Pause on `document.visibilitychange` (hidden), resume on visible. Cancel the rAF on unmount.
- Colours from CSS vars (`--color-bg`, `--color-ink`). No trails, blur or shadows **on the dots** (they'd put the
  motion signal into single frames).
- Accessibility: `role="img"` + `aria-label="Animated puzzle: a shape is hidden in moving dots. If you can't use
  motion puzzles, choose 'Verify with your account'."`. If `prefers-reduced-motion: reduce` → `autoplay=false`, show a
  "Play puzzle" button and the account link prominently.

## 4. `PactWidget` state machine
```
idle ──start──▶ loading ──ok──▶ round(0) ─pick─▶ round(1) ─pick─▶ round(2) ─pick─▶ submitting
  ▲               │err                                                          │
  │               ▼                                                  ┌──────────┴──────────┐
  └──retry── error(message)                                   passed(token)        failed(roundsCorrect)
                                                                   │                     │
                                                      onVerified(token)        "Try a new puzzle" → loading
expired (410) / already_answered (409) → error with "Get a new puzzle"
```
- `loading`: `api.createChallenge(cohort)`; show a skeleton the canvas size (no layout jump).
- `round(k)`: header "Round k+1 of 3"; canvas; `ShapeOptions` (6 buttons with icon + label, 44 px min target,
  keys **1–6**, arrow keys move focus, Enter selects). Record `timingsMs[k]` = click time − first frame drawn.
  Selecting advances immediately (no per-round correctness feedback).
- `submitting`: `api.submitAnswers(id, answers, timingsMs)`.
- `passed`: green check, "Verified human · token valid for 2:00" countdown → call `onVerified(token)`.
- `failed`: "Not quite: {roundsCorrect}/3 right. Humans usually get it on the first or second try." Buttons:
  **Try a new puzzle**, **Verify with your account instead**.
- `aria-live="polite"` region announces the round and results. Focus moves to the first option on each round.

## 5. Home (`/`): the story in one screen
- Brand: **ARHV** wordmark (text, no logo) + "Agent-Resistant Human Verification". Codename PACT appears nowhere
  in the UI.
- Hero: **"Agents can read any screen. They can't tilt your phone."** Sub: "ARHV checks that a person physically
  moved a real device, just now, for this request. Screen puzzles are a race AI agents are winning; physical
  proof is where verification has to go, and phone makers can make it unforgeable."
  CTAs: **Try it on your phone** (on laptops: shows the QR to `/phone`) · **Find a journey** (scrolls to the counter).
- **ARHV Rail counter (fictional demo)** card: route/date/class/quota controls with Bengaluru → Visakhapatnam defaults,
  followed by three fictional services. Button **Book this journey** → modal headed **Quick presence check** with
  **VerifyChooser** (§13) → on verified →
  `api.book(token)` → navigate to `/booking/confirmed`, where `BookingConfirmation` shows the fictional booking
  reference, seat, route, date, class, and "Allowed by Cedar policy `permit-physical-book`" (or
  `permit-motion-book`). A failed verification or 401/403 booking authorization renders the prominent
  "Suspicious activity detected. Please try human verification again." state with a fresh-challenge retry; route
  form values remain intact.
  Link under the button: *Can't use either? Verify with your account →* (`/account`, cut today: show the link only
  if the page exists).
- `DevPanel` (toggle "Show what AWS decided"): decoded token claims (`asr`, `prf`, `exp`, `jti`), the imu verifier
  `metrics` (tilt error °, gyro correlation, gravity fraction, samples, duration) when present, then
  `api.explain(token)` after booking → `DENY · forbid-token-replay` ("the same token can't be used twice"), and
  the last 5 API calls (method, path, status, ms). This panel is a video beat.
- "Three tiers" strip (static, 3 cards): **Perceptual** (motion puzzle, today's agents fail, not future-proof) ·
  **Physical** (phone tilt, built, unattested: simulators can pass) · **Vendor-attested** (the proposal: OS-signed
  gesture proofs, private tokens). Link to the README/PHYSICAL doc on GitHub.
- Scoreboard strip: "Humans (study): x/y · Best AI agent: x/y [CI] · Chance: 0.46%" (from `/v1/stats`; hide a cohort
  with N = 0; exact counts, no rounding up).

## 6. Lab (`/lab`)
- Controls: model select populated from `GET /v1/health › agentModels` (display names: `nova-2-lite` → "Amazon Nova 2 Lite",
  `nova-pro` → "Amazon Nova Pro", `claude` → "Claude on Amazon Bedrock"; unknown aliases shown as-is), frames segmented
  control (1 · 4 · 8, default 4), **Let the AI try**. If `cloudAgents` is false (local), show "Run `make bench
  BACKEND=ollama` locally" instead.
- `api.startAgentRun` → poll `api.getAgentRun` every 1.5 s (stop at done/error or 120 s). Progress: "Round 2 of 3:
  asking Amazon Nova 2 Lite…".
- `AgentRunView`: per round, side by side: **What the AI saw** (the K frames as `<img>` thumbnails from presigned
  URLs, 1:1 pixels, click to enlarge) and **What you see** (a live `MdgCanvas` of the *same* round, loaded once the
  run is done via `api.getAgentRun(runId, {replay: true})`, which regenerates the round from the stored seed). Then the
  AI's answer + confidence + rationale, truth + ✓/✗. Verdict banner: **AI FAILED (1/3)** in red, or **AI PASSED** in
  amber (be honest if it happens). This side-by-side is the key video moment.
- Full `Scoreboard`: table of all cohorts: attempts, pass rate [95% CI], round accuracy [95% CI], chance lines,
  "N is small; see the evaluation report" note linking to the GitHub `eval/report.md`.

## 7. About (`/about`)
How it works in 3 steps (with `docs/assets/screenshot-vs-motion.png` copied to `frontend/public/`), architecture
diagram (simple SVG/HTML boxes: Amplify → API Gateway → Lambda/Cedar → DynamoDB/S3/Secrets Manager/Cognito/Bedrock),
the three Cedar policies (code block), **honest limitations** (docs/SECURITY.md §4), accessibility statement,
credits and licences, "Built with Claude Code" AI-tools note.

## 8. `AccountVerify` (`/account`, lazy, Phase 4)
`Amplify.configure({ Auth: { Cognito: { userPoolId, userPoolClientId, loginWith: { email: true },
signUpVerificationMethod: "code" } } })` inside this module. `<Authenticator loginMechanisms={["email"]}>`; after
sign-in: `fetchAuthSession()` → `tokens.idToken.toString()` → `api.accountToken(idToken)` → keep the returned PACT
token in memory (React context) → navigate to `/` with state `{ token }` → booking proceeds; show "Account path ·
{bookingsToday}/2 today". Explain on the page why this path exists (WCAG 2.2 SC 3.3.8) and that it's rate-limited.

## 9. Design system (Best UI)
- Tokens (scaffold `index.css`): bg `#0b0d12`, surface `#121621`, surface-2 `#1a1f2e`, line `#262c3d`, ink `#e6e8ee`,
  muted `#9aa3b2`, accent `#f5a524` (saffron), ok `#22c55e`, bad `#ef4444`. Fonts: Inter (UI) + JetBrains Mono
  (tokens/ids) via Google Fonts `<link>` in `index.html` with `display=swap`.
- Radius 16 px cards / 12 px buttons; 1 px `line` borders; shadow only on the modal. 8-px spacing grid.
- Motion: 150–200 ms ease-out on state changes; honour `prefers-reduced-motion` everywhere.
- Contrast ≥ 4.5:1 for text (muted on bg passes). Focus ring: 2 px accent outline, offset 2.
- Mobile first: the widget fits 360×640 without scrolling during a round (canvas ≤ 88vw, options in a 3×2 grid).
- Icons: lucide-react for UI; shape icons only from `lib/shapes.ts`.
- Empty/loading/error states for every async call; never a blank screen.

## 10. API client rules (`lib/api.ts`)
- Base URL from `config.apiUrl` (no trailing slash). JSON in/out. Throw `ApiError(status, code, message)`.
- Log each call into a small in-memory ring buffer (DevPanel).
- Token handling: never persist PACT tokens; never log them to the console.

## 11. Env and deploy
- `make web-env` writes `.env.production.local` (+ `.env.development.local`) from stack outputs. Vite only exposes
  `VITE_*` and bakes them in at **build** time: rebuild after any change.
- `make web-deploy` builds and publishes to Amplify (manual zip deploy). URL: `https://main.<appId>.amplifyapp.com`.
- Local: `npm run dev` (http://localhost:5173) against the deployed API or `make local-api` (`write_frontend_env.py --local`).

## 12. Frontend tests (Vitest)
Keep `lib/mdg.test.ts` (scaffold). Add: `cohort.test.ts` (query → storage → header), `api.test.ts` (error mapping with a
mocked `fetch`), `PactWidget.test.tsx` (renders loading → round 1 with a stubbed client; keys 1–6 select; submits 3 answers).

## 13. Physical path (`imu-v1`): VerifyChooser, PhysicalWidget, `/phone`
**Existing, tested code (don't rewrite):** `lib/imu.ts` and `components/TiltChallenge.tsx`
(`<TiltChallenge challenge onDone={(trace) => …} onUnsupported={() => …} />`). TiltChallenge requests motion
permission **inside the tap handler** (iOS 13+ requires both `DeviceMotionEvent.requestPermission()` and
`DeviceOrientationEvent.requestPermission()` from a user gesture), records ~60 Hz samples, guides the dot into 3
rings, vibrates on each ring, and calls `onDone(trace)`; it never decides pass/fail.

**`VerifyChooser`** (modal body). `canTilt = typeof DeviceMotionEvent !== "undefined" &&
matchMedia("(pointer: coarse)").matches`.
- `canTilt` → first card **"Tilt your phone"** (physical proof, recommended), second **"Spot the shape"** (motion puzzle).
- otherwise → first **"Spot the shape"**, second **"Use your phone instead"**: a QR (`qrcode` npm,
  `QRCode.toDataURL(url, {margin: 1, width: 220})`) of `${location.origin}/phone` (+ `?cohort=` if set) with the
  caption "Scan with your phone camera. Tilting a real phone is something a screen-only AI can't do."
  Stretch (S5): the QR carries a handoff (`/phone?h=<handoffId>&k=<phoneKey>`) and the laptop polls
  `GET /v1/handoffs/{id}` every 1.5 s, then continues to booking with the delivered token.
**`PhysicalWidget` state machine**
```
idle ─start→ loading (POST /v1/challenges {family:"imu-v1"}) ─ok→ tilt (TiltChallenge) ─onDone→ submitting
submitting ─200 passed→ passed(token, metrics) → onVerified(token)
submitting ─200 failed→ failed(reasons, metrics) ─"Try again"→ loading (new challenge; old one is consumed)
any 409/410 → error("This check expired. Start a new one.") ; network → error(retry)
onUnsupported / permission denied → fallback card: "Motion sensors aren't available here" + "Spot the shape instead"
```
Failure copy (map `reasons`, most specific first):
| reasons contain | Message |
|---|---|
| `targets` | "You didn't reach all three rings in order. Try again: hold the dot inside each ring until it fills." |
| `timing` | "That took too long or the sensor stream stalled. Try again and keep the page open." |
| `gravity`, `tilt`, `gyro`, `continuity` | "Your device's sensors didn't behave like a phone moving in a hand. If you're emulating sensors, that's exactly what we check." |
| `binding`, `size`, `format` | "Something went wrong with this check. Start a new one." |
Show the `metrics` only in the DevPanel (not in the main card).

**`/phone` page** (`pages/Phone.tsx`, mobile-first, ≤ 360×640 without scrolling during the tilt):
counter summary → PhysicalWidget → `api.book(token)` → BookingCard (+ DevPanel toggle). Handoff mode (`?h=&k=`,
S5): the widget sends `{family: "imu-v1", handoffId, phoneKey}` and, on pass, shows **"Done. Return to your
computer."** with no booking on the phone.
**Platform notes:** sensors need HTTPS (Amplify URL; never plain `http://` LAN URLs). iOS: if the user taps
"Don't Allow", Safari may not ask again for this site until it's restarted, so show the motion-puzzle fallback.
Android Chrome streams without a prompt. In-app browsers (WhatsApp/Instagram) may block sensors: show "Open in
Chrome/Safari". Keep the page in portrait (the dot uses device axes).
**Tests (Vitest):** keep `lib/imu.test.ts`; add `reasons.test.ts` (reasons → message mapping, most specific first)
and, if time, `PhysicalWidget.test.tsx` with a stubbed API and a stubbed `TiltChallenge` that calls `onDone`.
**Dependency:** `npm install qrcode @types/qrcode` (log it in `MEMORY.md › Decisions`).
