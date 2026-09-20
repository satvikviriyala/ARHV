# HUMAN STEPS — only a person can do these (Claude Code: list them in MEMORY.md › Human-Blocked when reached)

**Today (Sun 20 Sep, deadline 20:00 IST) the blocking ones are H0, H15, H16, H11 and H13.**
| # | When | Step | How | Time |
|---|---|---|---|---|
| H0 | **Now (S0)** | **Give IAM user `liv28` enough permission** (it's denied `amplify:ListApps` and `budgets:ViewBudget` today) | Console (root/admin) → IAM → Users → `liv28` → Add permissions → Attach policies directly → **AdministratorAccess** → Add. Then `aws sts get-caller-identity`. Keys stay only in `~/.aws/credentials`. | 3 min |
| H1 | Done | Confirm the submission deadline | Sun 20 Sep 2026, 20:00 IST (MEMORY.md › Snapshot) | – |
| H2 | Done | AWS credentials on this machine, region us-east-1 | `aws configure` (liv28 access key) | – |
| H3 | Optional | Credits + student verification | Hackathon Google form; AWS Builder Center student verification (each member) | 5 min |
| H4 | Skip today | Bedrock Anthropic use-case form | Nova 2 Lite / Nova Pro already work; Claude is optional | – |
| H5 | Optional | Budget alarm email | Billing console or `aws budgets create-budget` (docs/AWS_INFRA.md §7) | 2 min |
| H6 | Done | GitHub repo | https://github.com/satvikviriyala/ARHV (public) | – |
| H15 | **After S2 deploy (~18:15)** | **Real-phone test of the tilt check** | Open the Amplify URL on your phone (HTTPS) → Book the last seat → Tilt your phone → Allow motion access (iPhone) → pass 3 times. Also an Android phone if anyone has one. If it fails, open "Show what AWS decided" and send Claude Code the `metrics` + `reasons` | 10 min |
| H16 | S3 (~18:30) | **3-person pilot** | Send `https://<amplify-url>/phone?cohort=study` (phones) and `https://<amplify-url>/?cohort=study` (laptop motion puzzle) to 3 friends nearby; note who passed on the first try | 15 min |
| H7 | Skip today | Larger human study | Beyond the 3-person pilot, after the deadline | – |
| H8–H10 | Skip today | LocalStack token, Ollama model, Cognito test account | Cut list (sprint §3) | – |
| H11 | S4 (18:50) | **Record + upload the video** | docs/DEMO_VIDEO.md (phone screen recording + a second camera on your hand) | 45 min |
| H12 | Skip today | Blog on AWS Builder Center | After submission if you want the side quest | – |
| H13 | S4 (by 19:45) | **Submit the form** | Repo, video, writeup; screenshot the confirmation | 10 min |
| H14 | Anytime | Approve destructive ops | e.g. `sam delete` after a failed first create; Claude Code never does this alone | 2 min |
