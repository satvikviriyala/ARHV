# PHASE 4: Accessible path + Build It on localhost (budget 3 h · Sun 12:00–15:00 IST)

**Goal:** (a) people who can't use motion puzzles can still book through a Cognito-verified account, rate-limited by
Cedar; (b) the whole system runs on localhost with open-source AWS tools, including a local Strands + Ollama red team.
**Read first:** `docs/ACCESSIBILITY.md`, `docs/FRONTEND.md §8`, `docs/AUTHZ_CEDAR.md §3–5`, `docs/LOCAL_DEV.md`.

## Part A: accessible path (≈ 1.5 h)
**4.1 `AccountVerify` page** (lazy route `/account`): configure Amplify Auth in this module only; `<Authenticator
loginMechanisms={["email"]}>`; after sign-in `fetchAuthSession()` → ID token → `api.accountToken(idToken)` → store
the PACT token in a small React context (memory only) → return to `/` and continue the booking. Page copy from
docs/ACCESSIBILITY.md §3; show "{bookingsToday}/2 today". Links to `/account` from the widget (every state), the
reduced-motion choice and the booking card.

**4.2 A11y pass:** reduced-motion flow (§2), keyboard-only run, aria-live announcements, focus returns to the
trigger when the modal closes, 200% zoom, 360 px width. Tick docs/ACCESSIBILITY.md §5 items in MEMORY Log.

**4.3 Deploy + verify (H10 account).** `make web-deploy`. With the test account: booking 1 → 201, booking 2 → 201,
booking 3 → 403; explain on the third token shows DENY with no permit (quota). Record in MEMORY.

## Part B: Build It on localhost (≈ 1.5 h)
**4.4** `make local-up` → `make local-api` (terminal 2) → `make local-smoke` green. Fix local-only issues via
docs/LOCAL_DEV.md §4. Point the dev UI at it (`write_frontend_env.py --local`, `npm run dev`) and complete one human
pass locally.

**4.5 Ollama red team (H9).** Choose the vision model by RAM (docs/REDTEAM_AGENT.md §2), confirm "vision" in
`ollama show <model>`, then `make bench BACKEND=ollama MODEL=<model> K=4 N=10 API=http://127.0.0.1:3000`
(N=5 if slow). JSONL goes to `eval/results/`. Log the model + licence (`ollama show <model> --license`).

**4.6 Cedar offline evidence.** `make cedar-demo > eval/cedar-demo.txt` and `.venv/bin/python -m pytest -q
backend/tests/test_authz.py`. Both are shown in the video's Build It beat.

**4.7 Optional LocalStack (H8).** Only with a token: `make local-up LOCAL_PROFILE=localstack`, `make local-api
LOCAL_PROFILE=localstack`, `make local-smoke LOCAL_PROFILE=localstack`. On any licence/auth error, stop (R12).

**4.8 Close.** Tests + lint green · MEMORY · `git tag phase-4-done` · push.

## Exit gate
- [ ] Account path on the live URL: 2 bookings allowed, 3rd denied by quota; reduced-motion users are offered it
- [ ] `make local-smoke` green; local UI completes a pass; Ollama bench JSONL exists; `eval/cedar-demo.txt` exists
