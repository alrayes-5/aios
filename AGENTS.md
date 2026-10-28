# AGENTS.md

This file tells any AI agent how to work in this workspace. It is the main file: Codex, OpenCode, Cursor and most other agent tools read `AGENTS.md`. Claude Code reads `CLAUDE.md`, which points here. It is loaded at the start of every session.

---

## What this is

AIOS, by Ahmed Elrayes. A plain-files workspace you open with an AI agent, again and again, so the AI always knows who you are, what the business is, and what matters now. It is personal by default and adapts to a company (see `example/`).

Five layers: **know, measure, think, act on its own, deliver.**

| Layer | What it is | Where it lives |
| ----- | ---------- | -------------- |
| 1. Context | What the business is: the owner, the strategy, the current state, the rules | `context/`, `/prime`, `/plan` |
| 2. Data | The numbers in one place, computed by a script | `data/`, `scripts/kpi.py`, `/kpi` |
| 3. Intelligence | Raw context turned into judgment: what matters, what slipped, what to do | `/daily-brief` |
| 4. Automation | Work that happens without a session: a scheduled brief | `automation/` |
| 5. Output | What leaves the workspace: drafts a person sends | `outputs/drafts/` |

---

## You and the user

- **The user** sets goals, supplies context, and decides. Nothing leaves the workspace without them.
- **You** read the context, run the commands, produce drafts and plans, and keep the workspace consistent.

Start every session with `/prime`. **Read `context/rules.md` before you act.** It says what you may do alone, what needs approval, and what data never goes in. When a rule gets in the way, stop and ask.

---

## Workspace structure

```
AGENTS.md  CLAUDE.md   instructions (CLAUDE.md points to AGENTS.md)
START_HERE.md          setup for people
context/               who, what, why: read by /prime. rules.md is what you may do
data/                  kpis.csv (readings) and targets.csv, changed only by scripts/kpi.py
commands/              the commands, written once as plain steps any agent can follow
.claude/ .opencode/    thin wrappers so they run as slash commands, and each tool's permissions
scripts/               kpi.py
automation/            a scheduled morning brief
plans/                 plans written by /plan
outputs/drafts/        drafts. You write, the user sends
reference/             templates and patterns worth reusing
example/               one made-up company, filled in, as a company setup
```

---

## Commands

Each command is a plain Markdown file in `commands/`. If your tool has no slash commands, read the file and follow its steps when the user types the command.

| Command | What it does |
| ------- | ------------ |
| `/prime` | Check the protected files, load the context, say back what you understood. Run first. |
| `/plan [request]` | Write a short plan in `plans/` before a bigger change, then do it after the user says go. |
| `/kpi [add \| define ...]` | Run `scripts/kpi.py`: show the status table, or record a reading. |
| `/daily-brief [focus]` | What matters, what slipped, what to do. Saves a draft in `outputs/drafts/`. |

---

## Protected files

These files change what every future session does, so the tool's permission rules stop you from editing them (Claude Code: `.claude/settings.json`; OpenCode: `opencode.json`): `AGENTS.md`, `CLAUDE.md`, `context/rules.md`, `commands/`, `scripts/`, `automation/`, `.claude/`, `.opencode/`, `opencode.json`, `.github/`.

If you are refused, do not look for another way. In particular, do not change them with a shell command, a script or a rename. Write the change you wanted as text in `plans/`, tell the user which file it is for, and let them apply it.

Shell commands that the tool does not treat as read-only need the user's approval. Never ask for broader permission, and never tell the user to turn permission prompts off.

The numbers are different: never edit `data/kpis.csv` or `data/targets.csv` by hand. Use `scripts/kpi.py` (through `/kpi`) so every reading has a date and a source.

Keep passwords and private files outside this folder. These rules are written for tools that enforce them (Claude Code, OpenCode). In any other tool they are instructions you follow by your own discipline.

---

## Keeping this workspace current

When you change the workspace, ask whether `AGENTS.md` should change too: a new command, a new folder, a new workflow. If yes, propose the new wording to the user (it is protected, so they apply it). Add a command by writing `commands/<name>.md` and the two wrappers: the user does this, since `commands/` is protected.

Do not edit the `context/` files without the user's confirmation. They are the user's words.

## Notes

- Keep context minimal but sufficient. Bloat makes every session slower.
- Plans carry a date in the filename: `plans/YYYY-MM-DD-name.md`.
- Never invent a number, a name or a date. If the files do not say, say "not in the files".
