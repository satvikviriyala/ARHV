# PHASE 6: Demo video + submission (budget 4 h · Sun 18:30–22:30 IST; buffer to 23:59)

**Goal:** a ≤ 3:00 YouTube video that shows every claim running on AWS, a sharp writeup, the blog, and a confirmed
submission well before the deadline.
**Read first:** `docs/DEMO_VIDEO.md`, `docs/SUBMISSION.md`, `docs/CONTEXT.md §5`.

## Tasks
**6.1 Feature freeze.** Only fixes from now on. Re-run `make smoke`. Make sure the Lab has a fresh completed run and
the scoreboard shows study + agent cohorts.

**6.2 Fill the script with real numbers.** Replace X/Y/Z in docs/DEMO_VIDEO.md from `eval/report.md` and the
Billing console (human reads the cost: Billing → Bills; note gross charges and credits). Put the final voiceover in
`docs/assets/voiceover.md`, and the exact terminal commands for the Build It beat in `docs/assets/demo-commands.md`.

**6.3 Recording support.** Warm-up script: one challenge, one booking, one Lab run right before recording. Open the
AWS console tabs listed in the script. The human records and edits (H11); keep ≤ 2:58; upload Public/Unlisted.

**6.4 Writeup.** Fill docs/SUBMISSION.md §2 with real numbers, links and the AI-tools list → `docs/assets/writeup.md`
(the human pastes it into the form). Every claim must be visible in the video; otherwise delete the claim.

**6.5 Blog.** Draft `docs/assets/blog-draft.md` per docs/SUBMISSION.md §4 (with the figure, architecture, results,
lessons). The human publishes it on AWS Builder Center (H12) and gives you the link.

**6.6 Final README touch.** Add the video link, blog link and final numbers. Commit and push. Confirm the repo is
public (open it logged out).

**6.7 Submit (H13).** Run docs/SUBMISSION.md §6 compliance checklist item by item; write the results in MEMORY. The
human submits/updates the form and screenshots the confirmation. Post the social update (§5).
`git tag v1.0-submission && git push --tags`.

**6.8 Close.** MEMORY: final Snapshot (all milestones ticked, links), Log. Leave the stack running for judges.

## Exit gate
- [ ] Video ≤ 3:00 on YouTube, plays logged-out, shows AWS (Amplify URL, console cuts, Bedrock run, Cedar decision)
- [ ] Writeup (problem, build, where AWS fits, learnings, AI tools, limitations) matches the video and the report
- [ ] Blog published and linked · repo public with README final · compliance checklist fully ticked
- [ ] Submission confirmed before the deadline (screenshot saved)
