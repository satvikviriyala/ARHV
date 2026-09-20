# DATA MODEL — one DynamoDB table (`pact-dev`; local `pact-local`)

Keys: `PK` (S, hash), `SK` (S, range). On-demand billing. TTL attribute: `ttl` (epoch seconds).
**Reserved words:** `STATUS`, `TTL`, `COUNT`, `DATA`, `NAME`, … Always alias attribute names in expressions:
`ExpressionAttributeNames={"#s": "status", "#ttl": "ttl", "#n": "n"}`.

## Items
| Entity | PK | SK | Attributes | TTL | Written by |
|---|---|---|---|---|---|
| Challenge | `CH#<challengeId>` | `META` | `family` (`mdg-v1`\|`imu-v1`), `seedHex` (server-only), `answers` (list, server-only; **mdg-v1 only**), `cohort`, `status` (`issued`→`answered`), `createdAt`, `expiresAt`, `answeredAt`, `handoffId` (imu-v1 via handoff only) | createdAt + 7 d | ApiFunction, AgentWorker |
| Stats counter | `STATS#<family>` | `COHORT#<cohort>` | `attempts`, `passes`, `roundsCorrect`, `roundsTotal`, `durationMsTotal`, `updatedAt` (numbers via `ADD`) | none | ApiFunction, AgentWorker |
| Used token | `JTI#<jti>` | `USED` | `usedAt`, `exp` | exp + 1 h | AuthorizerFunction |
| Account quota | `QUOTA#<sub>` | `<yyyy-mm-dd>` (UTC) | `n` (bookings that day) | +2 d | BookingFunction (ADD), Authorizer/AccountToken (read) |
| Booking (fictional) | `BOOKING#<bookingId>` | `META` | `pnr`, `seat`, `assurance`, `policy`, `sub`, `createdAt` | +7 d | BookingFunction |
| Agent run | `RUN#<runId>` | `META` | `status` (`queued`/`running`/`done`/`error`), `model`, `modelId`, `frames`, `progress`, `rounds` (list of maps), `passed`, `roundsCorrect`, `error`, `challengeId`, `createdAt`, `startedAt`, `finishedAt` | +7 d | ApiFunction (create), AgentWorker (update) |
| Daily agent cap | `LIMIT#agent-runs` | `<yyyy-mm-dd>` | `n` | +2 d | ApiFunction |
| Handoff (stretch) | `HO#<handoffId>` | `META` | `pollKeyHash`, `phoneKeyHash` (SHA-256 hex; never the keys), `status` (`pending`→`verified`→`delivered`), `token` (only while `verified`; REMOVEd on delivery), `challengeId`, `createdAt`, `expiresAt` (+300 s), `verifiedAt`, `deliveredAt` | createdAt + 1 d | ApiFunction |

Item size: a run with 3 rounds of rationale/frame keys is ≪ 400 KB. **Never** store PNG bytes or frames in DynamoDB
(frames → S3 `runs/<runId>/r<round>_f<frame>.png`). **Never store raw `imu-v1` sensor traces** anywhere (privacy:
motion data can fingerprint devices). The verifier's `metrics` go to the `imu_verified` log line; stats counters
use `STATS#imu-v1` (`roundsCorrect` = targets reached, `roundsTotal` = 3 per attempt).

## Access patterns → operations
| Need | Operation |
|---|---|
| Create challenge | `PutItem CH#id/META` |
| Consume challenge once, not expired | `UpdateItem … SET #s=:answered, answeredAt=:now` with `ConditionExpression="attribute_exists(PK) AND #s = :issued AND expiresAt >= :now"`, `ReturnValues="ALL_NEW"`; on `ConditionalCheckFailedException` → `GetItem` to decide 404/409/410 |
| Count an attempt | `UpdateItem STATS#mdg-v1/COHORT#c ADD attempts :one, passes :p, roundsCorrect :k, roundsTotal :n, durationMsTotal :d SET updatedAt=:now` |
| Read stats | `Query PK = STATS#<family>` (`mdg-v1` or `imu-v1`) |
| Single-use token | `PutItem JTI#jti/USED` with `ConditionExpression="attribute_not_exists(PK)"` → failure means replay |
| Explain (no side effects) | `GetItem JTI#jti/USED` |
| Account quota | `GetItem QUOTA#sub/<date>`; `UpdateItem ADD #n :one ReturnValues=UPDATED_NEW` after an ALLOWed booking |
| Agent daily cap | `UpdateItem LIMIT#agent-runs/<date> ADD #n :one` with `ConditionExpression="attribute_not_exists(#n) OR #n < :cap"` |
| Run lifecycle | `PutItem RUN#id/META` then `UpdateItem SET …` after each round |
| Handoff: phone binds | `GetItem HO#id/META`; compare `phoneKeyHash`, `#s = pending`, not expired → store `handoffId` on the `CH#` item |
| Handoff: verified | `UpdateItem SET #s=:verified, #tok=:t, challengeId=:c, verifiedAt=:now` with `ConditionExpression="#s = :pending AND phoneKeyHash = :pk AND expiresAt >= :now"` (`#tok` aliases `token`, `#s` aliases `status`) |
| Handoff: deliver once | `UpdateItem SET #s=:delivered, deliveredAt=:now REMOVE #tok` with `ConditionExpression="#s = :verified AND pollKeyHash = :h"`, `ReturnValues="ALL_OLD"` → the old image carries the token; a failed condition → re-read to answer `pending`/`delivered`/404 |

## Example items
```json
{"PK":"CH#ch_3f9c…","SK":"META","family":"mdg-v1","seedHex":"9b…","answers":["star","heart","plus"],
 "cohort":"study","status":"issued","createdAt":1789999000,"expiresAt":1789999180,"ttl":1790603800}
{"PK":"STATS#mdg-v1","SK":"COHORT#agent:nova-2-lite:k4","attempts":30,"passes":0,"roundsCorrect":16,
 "roundsTotal":90,"durationMsTotal":0,"updatedAt":1789999999}
{"PK":"JTI#4c1d…","SK":"USED","usedAt":1789999050,"exp":1789999120,"ttl":1790002720}
{"PK":"CH#ch_a71e…","SK":"META","family":"imu-v1","seedHex":"5e…","cohort":"public","status":"issued",
 "createdAt":1789999000,"expiresAt":1789999180,"ttl":1790603800}
{"PK":"HO#ho_9b2f…","SK":"META","pollKeyHash":"c3…","phoneKeyHash":"8d…","status":"pending",
 "createdAt":1789999000,"expiresAt":1789999300,"ttl":1790085400}
```
(Illustrative values only.)

## Local tables
`scripts/local_bootstrap.py` creates `pact-local` with the same key schema in DynamoDB Local (`:8000`) or
LocalStack (`:4566`). TTL isn't enforced locally; that's fine.
