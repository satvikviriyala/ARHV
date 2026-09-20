# ACCESSIBILITY — fair to humans, not just hard for bots

## 1. Standards mapping
| WCAG 2.2 | Requirement | PACT |
|---|---|---|
| **3.3.8 Accessible Authentication (Minimum), AA** | A cognitive function test needs an alternative (or falls under the object-recognition exception) | Shape recognition = object recognition, **plus** a non-cognitive alternative: Cognito-verified account path |
| 1.1.1 Non-text Content | CAPTCHA must say what it is and offer another modality | Canvas `aria-label` states the purpose and points to the account path |
| 2.1.1 Keyboard | Everything operable by keyboard | Options on keys 1–6, arrows move focus, Enter selects; visible focus ring |
| 2.2.2 Pause, Stop, Hide | Moving content must be pausable, unless the motion is essential | Motion is the test itself (essential); we pause when the tab is hidden; reduced-motion users get the choice first |
| 2.3.1 Three Flashes | No more than 3 flashes/second | No flashing: dot motion at constant luminance; ping-pong playback has no strobe; never add flicker effects |
| 1.4.3 Contrast | ≥ 4.5:1 text | Tokens chosen to pass; dots ≈ 16:1 on background |
| 2.5.8 Target Size (Minimum) | ≥ 24 px targets | Option buttons ≥ 44 px |
| 4.1.3 Status Messages | Announce changes | `aria-live="polite"` for rounds and results |

## 2. Reduced motion
If `matchMedia("(prefers-reduced-motion: reduce)")` matches: don't autoplay the puzzle; show two equal choices:
**Play the motion puzzle** and **Verify with your account**. Never force motion on these users.

## 3. The account path (Phase 4)
Email + code sign-up/sign-in (Cognito) → `POST /v1/tokens/account` → token `asr=account` → Cedar allows up to 2
bookings per day. Page copy: "Can't use motion puzzles? Verify with a confirmed account instead. No puzzle, just
your email. This path is limited to 2 bookings per day." Desktop widgets and booking cards link to this route;
`/phone` remains a sensor-only flow, while the account route stays available separately.

## 4. Copy guidelines
Plain language; no blame ("Not quite", never "Wrong!" or "Are you a robot?"). Say how long it takes ("about 10
seconds"). Explain why the account path exists.

## 5. Test checklist (Phase 4/5; record in MEMORY.md)
- [ ] Keyboard-only completion. [ ] VoiceOver/NVDA announces round changes and results.
- [ ] Reduced-motion flow. [ ] 200% zoom: no clipping. [ ] Phone portrait at 360 px wide.
