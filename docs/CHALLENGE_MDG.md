# CHALLENGE — Motion-Defined Glyph (`mdg-v1`)

Reference implementation (tested): `docs/reference/scaffold/backend/layers/core/pact_core/mdg.py`.
Tests: `docs/reference/scaffold/backend/tests/test_mdg.py`. Figure: `docs/assets/screenshot-vs-motion.png`.

## 1. Principle (use this wording in the About page and video)
Two independent random-dot textures cover the canvas. Inside a hidden shape we show dots from texture **F**, which
drifts one way. Outside it we show dots from texture **G**, which drifts (near-)opposite. Both textures have the same
density, so **any single frame is statistically uniform noise**: the shape isn't in the pixels of any screenshot.
It exists only in *how the dots move between frames*. Human vision groups dots that move together (the Gestalt law
of "common fate"; motion-defined form is processed early in visual cortex), so people see the shape pop out
instantly. A screenshot-driven agent sees snow.

## 2. Parameters (constants in `mdg.py`; change only via the tuning rules in §7)
| Constant | Value | Why |
|---|---|---|
| `W = H` | 160 logical px | Small payload; the client scales it up with CSS (`image-rendering: pixelated`) |
| `DOT` | 2 px | Visible at 2.5× scale on phones; still dense |
| `SPAN` | 159 | Valid top-left coordinates 0..158 (dot stays inside the canvas) |
| `N_DOTS` | 600 per texture | ≈ 9% coverage: dense enough for a strong percept, sparse enough to stay noise-like |
| `FRAMES` | 36 per round | 1.2 s of motion; client plays ping-pong (0→35→0…) at 30 fps, so there's no loop jump |
| `ROUNDS` | 3 | Pass = all 3 correct. Chance = (1/6)³ ≈ 0.46% |
| `N_OPTIONS` | 6 (1 correct + 5 distractors) | Chance per round 16.7% |
| `NOISE` | 0.15 | 15% of dots re-drawn randomly every frame: breaks naive dot tracking; humans barely notice |
| Shapes | circle, square, triangle, star, plus, heart, arrow, moon | Distinct silhouettes; icons generated from the same geometry (IoU ≥ 0.999) |
| Shape radius / centre | 46–56 px / centre ± 12 px | Large, never clipped; position varies |
| Rotation | ±25° (arrow: + a multiple of 90°) | Avoids a canonical pose without hurting recognition |
| Velocities | figure: one of 8 compass directions at 1 px/frame (diagonals √2); ground: opposite ± 45° | Strong kinetic boundary |

## 3. Algorithm (what `generate_challenge(seed)` does)
1. `seed` = 32 bytes from `secrets.token_bytes(32)` (server only). Three independent streams:
   `KeyedRng(seed,"spec")`, `KeyedRng(seed,"tex")`, `KeyedRng(seed,"noise")`, each SHAKE-256(seed|label|counter).
2. Per round, `make_round_spec` picks the shape, centre, radius, rotation, figure/ground velocities and the 6 shuffled options.
3. `make_mask` rasterises the shape at dot centres into a 160×160 bytemask.
4. `render_round`: draw `0.85·N` dots for F and `0.85·N` for G at random positions. For frame t, shift F by
   `fig_v·t` and G by `gnd_v·t` (wrap-around), keep F-dots inside the mask and G-dots outside, add `0.15·N` fresh
   random noise dots, then **shuffle** the frame's dot list (order carries no identity).
5. Encode (below). Return `{"public": …, "answers": [...], "specs": [...]}`. Only `public` goes to clients.

## 4. Wire format (`public.rounds[i].frames`)
Per round, one base64 string: for each frame `[uint16 big-endian count][count × (uint8 x, uint8 y)]`, concatenated.
`x, y ∈ [0, 158]` are the dot's top-left corner in logical px. The client draws `fillRect(x, y, DOT, DOT)`.
Decoder: `frontend/src/lib/mdg.ts › decodeFrames` (reference, tested). Payload ≈ 170 KB JSON for 3 rounds.

`public` object:
```json
{ "family": "mdg-v1", "width": 160, "height": 160, "dot": 2, "fps": 30, "playback": "pingpong",
  "rounds": [ { "frames": "<base64>", "frameCount": 36, "options": ["star","moon","plus","circle","arrow","heart"] }, … ] }
```

## 5. Client rendering contract (MdgCanvas; details in docs/FRONTEND.md)
- Internal canvas 160×160; CSS size `min(88vw, 420px)` square; `image-rendering: pixelated`.
- Background `#0b0d12`, dots `#e6e8ee` (contrast ≈ 16:1). Clear then draw every frame.
- Frame index = `pingPongIndex(floor(elapsedMs × fps / 1000), frameCount)`. Use `requestAnimationFrame`; pause
  when `document.hidden`.
- Never pre-blend, blur or trail frames (that would put the motion signal into single frames).
- `prefers-reduced-motion: reduce` → don't autoplay: show "Play puzzle" and offer the account path (docs/ACCESSIBILITY.md).

## 6. Security properties (enforced by tests; keep them green)
| Property | Test |
|---|---|
| Deterministic per seed; different seeds → different challenges | `test_deterministic_for_same_seed_and_different_for_new_seed` |
| Public payload has no answers/specs/seed/mask; the answer is always among 6 unique options | `test_public_payload_never_contains_answers_or_specs` |
| **Single frames carry no shape signal:** dot density inside the secret mask matches its area (z-scores ≈ N(0,1); mean \|z\| < 0.25 over 180 frames) | `test_single_frame_carries_no_shape_signal` |
| Motion carries the signal: > 75% of figure-velocity-consistent dot pairs sit inside the mask | `test_motion_reveals_the_shape` |
| Encoding round-trips; answer checking is strict | `test_encoding_roundtrip`, `test_check_answers` |
| Fast enough for Lambda (< 2 s; ≈ 0.1 s locally) | `test_generation_is_fast_enough_for_lambda` |
| Unpredictable randomness | design: `KeyedRng` only; never `random.Random` in `pact_core` |

## 7. Tuning rules (decide from data, log every change in MEMORY.md › Decisions)
Pilot with ≥ 3 humans in Phase 2 and ≥ 20 agent runs in Phase 3. Then:
| Observation | Action (one knob at a time; re-run pilot) |
|---|---|
| Human round accuracy < 90% or pass rate < 80% | NOISE 0.15 → 0.08; radius 46–56 → 52–60; FRAMES 36 → 48; check icons are legible; add "Look for the patch moving differently" hint |
| Humans say it's "flickery"/tiring | NOISE → 0.10; keep speed at 1 px/frame; never add flashing |
| Agent **round** accuracy significantly above chance (Wilson lower bound > 0.25 at N ≥ 60 rounds) | NOISE 0.15 → 0.25; ground direction random (not near-opposite); add "limited dot lifetime" (re-spawn each dot every 6 frames). Re-check the human pilot |
| Payload too slow on mobile | FRAMES 36 → 24 and N_DOTS 600 → 450 (keep NOISE) |
| A scripted optical-flow attack (stretch) succeeds | Expected; document it. Mitigations: per-challenge parameter jitter, family rotation (§8), rate limits |

## 8. Future families (mention as roadmap, don't build this weekend)
- `mdg-v2`: shape moves as well as its texture (structure-from-motion).
- `occlusion-count`: count objects that pass behind an occluder over time.
- `biological-motion`: which way is a point-light walker facing? (humans excel; agents need temporal integration).
Rotation across families keeps a bespoke solver's cost recurring.
