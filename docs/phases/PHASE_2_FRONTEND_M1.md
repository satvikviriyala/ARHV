# PHASE 2: Frontend + Amplify → M1 (budget 4 h · Sat 21:00–01:00 IST)

**Goal (M1):** on the live Amplify URL, on a phone, a human passes 3 rounds and books the seat; the failure path
works; the Dev Panel shows the token and the Cedar decision. Then the human study starts (H7).
**Read first:** `docs/FRONTEND.md` (all), `docs/CHALLENGE_MDG.md §1, §5, §7`, `docs/ACCESSIBILITY.md`, `docs/API.md`.

## Tasks
**2.1 Foundations.** Google Fonts `<link>` (Inter 400/500/600/700, JetBrains Mono 400) in `index.html`;
`src/config.ts` (validate `VITE_API_URL`, `VITE_REGION`, `VITE_USER_POOL_ID`, `VITE_USER_POOL_CLIENT_ID`; render a
clear error screen if missing); `lib/api.ts` (all routes, `ApiError`, 20 s timeout, call log ring buffer);
`lib/cohort.ts`; `lib/jwt.ts`; `lib/format.ts`. Tests: `cohort.test.ts`, `api.test.ts` (mock `fetch`).

**2.2 Shell.** `main.tsx` with `createBrowserRouter`: `/` Home, `/lab` Lab (placeholder "Phase 3"), `/about` About
(placeholder), `/account` lazy placeholder. `Layout` with Header (logo "PACT", links Demo · Lab · About) and Footer
(repo link, "Built on AWS", "fictional demo" note). Replace the scaffold `App.tsx`.

**2.3 `MdgCanvas`** per docs/FRONTEND.md §3 (rAF loop, ping-pong, pause when hidden, reduced motion, aria-label).
Check it against the real deployed API: `cd frontend && npm run dev` (uses `.env.development.local` from
`make deploy`; CORS already allows `http://localhost:5173`). You should *see* the shape in motion.

**2.4 `ShapeOptions` + `PactWidget`** state machine per §4 (keys 1–6, focus management, timings, aria-live, errors
404/409/410). Test `PactWidget.test.tsx` with a stubbed API client.

**2.5 Home page:** hero, Rush Hour Counter card (fictional, labelled), modal with the widget, `BookingCard`
(PNR, seat, "Allowed by Cedar policy `…`"), `DevPanel` (claims; explain after booking → `forbid-token-replay`;
API log), `Scoreboard` strip from `/v1/stats` (hide cohorts with N = 0). Copy exactly as docs/FRONTEND.md §5.

**2.6 Human pilot (local).** You + ≥ 2 people solve on `localhost:5173` using cohort `public`. Record results in
MEMORY Log. Any person failing twice in a row → apply docs/CHALLENGE_MDG.md §7 easing, re-run backend tests (they
use the constants), redeploy, re-pilot.

**2.7 Deploy the web app.** `make web-env && make web-deploy` → `https://main.<appId>.amplifyapp.com`. Check: deep
link `/about` loads (SPA rewrite); a phone on 4G can complete the flow; no console errors; CORS OK.

**2.8 M1 verification + study.** Complete the flow on a real phone and on desktop; keyboard-only once. Then ask the
human to send the study link (H7): `https://main.<appId>.amplifyapp.com/?cohort=study`. Tick M1 in Snapshot.

**2.9 Close.** `make lint && make test` green · MEMORY · `git tag phase-2-done` · push.

## Exit gate
- [ ] **M1** on the live URL (desktop + phone): pass → booking card → Dev Panel explain shows DENY `forbid-token-replay`
- [ ] Failure path ("Not quite: k/3") and "Try a new puzzle" work; 410/409 handled
- [ ] Reduced-motion users aren't autoplayed; keyboard 1–6 works; lint + tests green; `make smoke` still green
- [ ] Study link sent (H7) and recorded in MEMORY

## If things go wrong
Blank page → `config.ts` error screen tells you which `VITE_*` is missing (`make web-env`, rebuild). CORS → R7.
Canvas looks static → you're drawing one frame; check the rAF loop and `pingPongIndex`. Shape hard to see → §7 easing.
