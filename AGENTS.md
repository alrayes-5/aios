# AGENTS.md

This file tells any AI agent how to work in this workspace. It is the main file: Codex, OpenCode, Cursor and most other agent tools read `AGENTS.md`. Claude Code reads `CLAUDE.md`, which points here. It is loaded at the start of every session.

---

## What this is

AIOS, the AI Operating System, by Ahmed Elrayes. A plain-files workspace you open with an AI agent, again and again, so the AI always knows who you are, what the business is, and what matters now. It is personal by default and adapts to a company (see `example/`).

Five layers: **know, measure, think, act on its own, deliver.**

| Layer | What it is | Where it lives |
| ----- | ---------- | -------------- |
| 1. Context | What the business is: the owner, the strategy, the current state, the rules | `context/`, `/prime` |
| 2. Data | The numbers in one place | `data/kpi-tracker.md`, `/kpi` |
| 3. Intelligence | Raw context turned into judgment: what matters, what slipped, what to do | `/daily-brief` |
| 4. Automation | Work that happens without a session: guard, session start, scheduled brief | `.aios/`, `automation/` |
| 5. Output | What leaves the workspace: drafts a person sends | `outputs/drafts/` |

---

## You and the user

- **The user** sets goals, supplies context, and decides. Nothing leaves the workspace without them.
- **You** read the context, run the commands, produce drafts and plans, and keep the workspace consistent.

Start every session with `/prime`. Then act with full awareness of who the user is and what they are working toward.

**Read `context/rules.md` before you act.** It says what you may do alone, what needs approval, and what data never goes in. When a rule gets in the way, stop and ask.

---

## Workspace structure

```
.
├── AGENTS.md              This file: main instructions
├── CLAUDE.md              One line that points Claude Code here
├── START_HERE.md          Setup for people
├── context/               Layer 1: who, what, why (read by /prime)
│   ├── personal-info.md
│   ├── business-info.md
│   ├── strategy.md
│   ├── current-data.md
│   └── rules.md           What you may do alone, what needs approval, what never goes in
├── data/                  Layer 2: kpi-tracker.md
├── commands/              The commands, written once as plain steps (any agent can follow them)
├── .claude/commands/      Thin wrappers so the commands run as slash commands in Claude Code
├── .opencode/commands/    The same wrappers for OpenCode
├── .aios/                 Layer 4: guard.py, session-start.py, guard.json
├── automation/            Layer 4: a scheduled morning-brief example
├── plans/                 Plans written by /create-plan
├── outputs/drafts/        Layer 5: drafts. You write, the user sends
├── reference/             Templates and patterns worth reusing
├── private/               The user's own files. Closed to you: never read or write here
├── scripts/               Aliases and helper scripts
└── example/               One made-up company, filled in, as a company setup
```

---

## Commands

Each command is a plain Markdown file in `commands/`. If your harness has no slash commands, read the file and follow its steps when the user types the command.

| Command | What it does |
| ------- | ------------ |
| `/prime` | Load the context and say back what you understood. Run first. |
| `/create-plan [request]` | Write a plan in `plans/` before any structural change. |
| `/implement [plan-path]` | Execute a plan and update its status. |
| `/kpi [add \| define ...]` | Show or update `data/kpi-tracker.md`. |
| `/daily-brief [focus]` | What matters, what slipped, what to do. Saves a draft in `outputs/drafts/`. |

---

## Protected files (the guard)

A guard checks every tool call in Claude Code and OpenCode (Bash and PowerShell commands included). It blocks:

- reads and writes of `private/`, including recursive searches from the workspace root that would walk into it (name a folder such as `context/`, or exclude `private/`);
- any write outside this folder;
- any edit to a core file: `AGENTS.md`, `CLAUDE.md`, `context/rules.md`, `opencode.json`, `.ignore`, `.aios/`, `.claude/settings.json`, `.opencode/plugins/`.

The guard reads the text of shell commands. It is not a sandbox, and you must not try to get around it.

If you are blocked, do not look for another way around it. Write the change you wanted as text in `plans/`, tell the user which file it is for, and let them apply it. The user can open a maintenance session with `AIOS_UNLOCK=1` to edit core files; `private/` stays closed even then.

If the harness has no guard (any tool other than Claude Code and OpenCode), the same rules apply by your own discipline.

---

## Keeping this workspace current

When you change the workspace, ask whether `AGENTS.md` should change too: a new command, a new folder, a new workflow. If yes, propose the new wording to the user (it is a core file, so you cannot edit it). Add a new command by writing `commands/<name>.md` and copying the two wrappers from an existing command.

Do not edit the `context/` files without the user's confirmation. They are the user's words.

---

## Session workflow

1. **Start:** `/prime`.
2. **Work:** run commands or take tasks directly.
3. **Plan changes:** `/create-plan` before anything structural.
4. **Execute:** `/implement`.
5. **Deliver:** drafts go to `outputs/drafts/`. A person sends them.

## Notes

- Keep context minimal but sufficient. Bloat makes every session slower.
- Plans carry a date in the filename: `plans/YYYY-MM-DD-name.md`.
- Never invent a number, a name or a date. If the files do not say, say "not in the files".
