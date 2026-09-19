# HUMAN STEPS — only a person can do these (Claude Code: list them in MEMORY.md › Human-Blocked when reached)

| # | When | Step | How | Time |
|---|---|---|---|---|
| H1 | Before Phase 0 | Confirm the **submission deadline** | https://www.wemakedevs.org/aws/first-commit/schedule, Discord or email → tell Claude Code; it goes into MEMORY.md | 2 min |
| H2 | Phase 0 | **AWS credentials** on this machine, region us-east-1 | `aws configure` (IAM user access key) or `aws configure sso`; verify `aws sts get-caller-identity` | 5 min |
| H3 | Phase 0 | **Credits + student verification** | Claim the $100 team credits via the hackathon Google form; submit AWS Builder Center student verification (each member) | 5 min |
| H4 | Phase 0 (early; approval can take a while) | **Bedrock Anthropic use-case form** (only if you want Claude as the strongest attacker) | Bedrock console (us-east-1) → Model catalog → an Anthropic Claude model → submit the use-case form | 3 min |
| H5 | Phase 0 | **Budget alarm email** | Give Claude Code your email for `aws budgets create-budget` (docs/AWS_INFRA.md §7) or create it in the Billing console | 2 min |
| H6 | Phase 0 | **GitHub repo** | `gh auth login` then let Claude Code run `gh repo create pact --public --source . --push`, or create an empty public repo and give Claude Code the URL | 3 min |
| H7 | Right after M1 (Sat night) | **Human study** | Send `https://<amplify-url>/?cohort=study` with the WhatsApp text in docs/EVALUATION.md §3 to 10+ friends | 5 min |
| H8 | Phase 4 (optional) | **LocalStack token** | Sign up at localstack.cloud (free non-commercial/student) → `export LOCALSTACK_AUTH_TOKEN=…` in your shell (don't paste it in chat) | 5 min |
| H9 | Phase 4 | **Ollama + a vision model** | Install from ollama.com; `ollama pull qwen2.5vl:7b` (≥ 16 GB RAM) or `gemma3:4b` | 10 min (download) |
| H10 | Phase 4 | **Cognito test account** | Sign up on `/account` with a real inbox; enter the code | 3 min |
| H11 | Phase 3 (early submission) and Phase 6 | **Record + upload the video** | docs/DEMO_VIDEO.md; YouTube Public/Unlisted | 2–3 h (final) |
| H12 | Phase 6 | **Blog** on AWS Builder Center | Paste/adapt Claude Code's draft (docs/SUBMISSION.md §4), publish, share link | 30 min |
| H13 | Phase 3 + Phase 6 | **Submit the form** (early, then final) | Hackathon submission form: repo, video, writeup, blog link; screenshot the confirmation | 10 min |
| H14 | Anytime a deploy needs cleanup | Approve destructive ops | e.g. `sam delete` after a failed first create (R5); Claude Code never does this alone | 2 min |
