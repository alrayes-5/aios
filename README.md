# AIOS: the AI Operating System

A free starter kit by **Ahmed Elrayes**. Plain files and a few commands that turn any AI agent into one that knows your business and starts every session informed. Personal by default, adapts to a company.

**Know, measure, think, act on its own, deliver.** Five layers, one working starter for each:

| Layer | Starter in this kit |
| ----- | ------------------- |
| 1. Context: what the business is | `AGENTS.md`, `context/` (4 files + `rules.md`), `/prime`, `/create-plan`, `/implement`, a private folder |
| 2. Data: the numbers in one place | `data/kpi-tracker.md`, `/kpi` |
| 3. Intelligence: raw context into judgment | `/daily-brief`: what matters, what slipped, what to do |
| 4. Automation: work without a session | a guard hook, a session-start hook, a scheduled morning brief (cron, or Task Scheduler on Windows) |
| 5. Output: what leaves the workspace | `outputs/drafts/`: the AI writes drafts, a person sends them |

Built for Claude Code and OpenCode, and usable with any other AI tool: give it the folder and a ready prompt (no guard there). Claude Code counts as tested on two grounds only: Ahmed Elrayes tested the template in Claude Code, OpenCode, AlphaCode and Codex on Windows, and a live run of this kit in Claude Code 2.1.312 on his Windows PC worked for the template and found guard problems, which are fixed. The guard and hooks were not part of his tests; they were tested in OpenCode on Linux. [START_HERE.md](START_HERE.md) lists exactly what was tested and what was not.

## Start

Read **[START_HERE.md](START_HERE.md)**. Set up the `cs` and `cr` aliases first, then pick your path.

## What is in here

```
AGENTS.md          main instructions (CLAUDE.md points to it)
START_HERE.md      setup, in order
context/           who you are, the business, strategy, current state, rules
data/              KPI tracker
commands/          the commands, written once as plain steps
.claude/ .opencode/  thin wrappers and settings for Claude Code and OpenCode
.aios/             the guard and the session-start script
automation/        a scheduled morning brief
example/           one made-up company, filled in, as a company setup
```

## Credits and licence

- AIOS is by Ahmed Elrayes, under the [MIT licence](LICENSE).
- `.claude/skills/skill-creator/` was originally Anthropic's `skill-creator`, adapted by OpenAI for Codex, and taken from OpenClaw's bundled copy; it is changed here only for AIOS ("Codex" to "the agent", punctuation). It is under the Apache License 2.0: its `license.txt` is kept and `NOTICE.md` says the same. Thank you, Anthropic, OpenAI and OpenClaw.
