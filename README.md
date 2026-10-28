# AIOS

A free starter kit by **Ahmed Elrayes**: plain files and four commands that make an AI agent know you and your business at the start of every session. For Claude Code, OpenCode or any other AI tool.

This is what `/daily-brief` printed in the made-up bakery company in `example/` (Claude Sonnet 5.5 following `commands/daily-brief.md`, see TESTING.md):

```text
# Daily brief, 2026-10-28

## Matters
1. On-time wholesale deliveries (priority 1): 91% against a 98% target, gap -7, change -8, behind. Two deliveries were late last week because of a van repair (context/current-data.md).
2. Bread waste (priority 2): 6.2% against 5%, gap +1.2, change -0.9, behind but improving.
3. Wholesale accounts (priority 3): 12 against 14, gap -2, behind. A hotel kitchen asked for a sample box on 22 October and three accounts asked for larger December orders; none answered or confirmed.

## Slipped
- Behind target in the status table: loaves baked (2380 vs 2400), bread waste, on-time deliveries, active wholesale accounts, shop revenue.
- Oven full inspection is due by 7 November and is not booked (context/current-data.md).
- Hotel kitchen sample box: asked 22 October, no reply sent (context/current-data.md).
- No STALE readings: every reading is 2 days old.

## Do
1. Dana: book the oven inspection before 7 November. Why: due date is close. Needs approval from Leo if it involves spending.
2. Me: draft the reply to the hotel kitchen about the sample box. Why: waiting since 22 October. Dana reviews and sends.
3. Dana: check what else, beyond the van repair, caused the late deliveries. Why: on-time delivery is behind its target.

## Gaps
- Cause of the late deliveries beyond the van repair: not in the files.
- Cost of the oven inspection: not in the files.
- No plans or earlier drafts exist.
```

**Start:** [START_HERE.md](START_HERE.md), about 15 minutes. **Update:** [UPDATING.md](UPDATING.md). **What was tested, and what was not:** [TESTING.md](TESTING.md). **Changes:** [CHANGELOG.md](CHANGELOG.md).

**Safe by default:** Claude Code and OpenCode ask before a shell command, and cannot edit the files that steer them (`AGENTS.md`, `commands/` and a few more). In any other tool those are instructions, not enforced rules.

By Ahmed Elrayes, under the [MIT licence](LICENSE).
