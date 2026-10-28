# Start here

AIOS is a folder of plain files. You open an AI agent in that folder, and the agent reads the files first, so it knows who you are, what your business is and what matters now. This page gets you from zero to a first session. Allow about 15 minutes.

Five layers, one working starter each: **know, measure, think, act on its own, deliver.** The table is in [README.md](README.md).

## 0. Before you begin

- A folder on your own computer. Put this kit in it: `git clone https://github.com/alrayes-5/aios.git ~/aios` (or download the ZIP and unpack it to `~/aios`).
- Python 3.8 or newer. The guard (step 4) is a small Python script. Check with `python3 --version` (on Windows: `python --version` or `py --version`). On Windows install Python from [python.org](https://www.python.org/downloads/) and tick "Add python.exe to PATH"; the Microsoft Store shortcut named `python3` does not run scripts. The guard tries `python3`, then `python`, then `py`, and blocks every action if none of them runs.
- On Windows, also [Git for Windows](https://git-scm.com/download/win). Claude Code's hooks are short shell commands, and Git Bash runs them there. Windows without Git Bash was not tested.
- One of: [Claude Code](https://code.claude.com/docs) (paid account), [OpenCode](https://opencode.ai) (free, works with free models), or your own AI tool of any kind (Path C).

## 1. Set up `cs` and `cr` first

These two commands are step 1 of AIOS. They open Claude Code in your workspace and run `/prime` for you.

**macOS and Linux:** add two aliases to your `~/.zshrc` or `~/.bashrc`:

```bash
alias cs='claude "/prime"'
alias cr='claude --dangerously-skip-permissions "/prime"'
```

Reload your shell with `source ~/.zshrc`.

**Windows (PowerShell):** open your profile with `notepad $PROFILE` (if it says the file does not exist, run `New-Item -Force $PROFILE` first), add two functions, save, and reload with `. $PROFILE`:

```powershell
function cs { claude "/prime" }
function cr { claude --dangerously-skip-permissions "/prime" }
```

If PowerShell refuses to load the profile, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

From now on: go to your AIOS folder (for example `cd ~/aios`, or `cd $HOME\aios` on Windows), then type `cs`.

- **`cs`** (Claude Safe): Claude asks before it changes a file or runs a command. Use it while you learn the kit.
- **`cr`** (Claude Run): Claude Code does not ask. It is faster, and it is only as safe as the guard in step 4. Use it in this folder only, and only for work you would let the AI do while you are away.

More in [scripts/shell-aliases.md](scripts/shell-aliases.md). OpenCode and other AI tools have no `cs`/`cr`; their paths are below.

## 2. Fill in your context (the same for all three paths)

Open these five files and replace the text in `[brackets]` with your own words. Short is fine. The AI reads them at the start of every session.

| File | What goes in |
| ---- | ------------ |
| `context/personal-info.md` | Who you are, your role, how you like to work |
| `context/business-info.md` | What the business is, what it sells, to whom |
| `context/strategy.md` | Your goals and priorities now |
| `context/current-data.md` | The current state: what is going on this month |
| `context/rules.md` | What the AI may do alone, what needs your approval, what data never goes in. Read it and change it to fit you |

You can also let the AI ask you the questions: run `/prime` and say yes when it offers to fill the files in. It writes an answer only after you confirm it.

To see a finished version first, open `example/`: one made-up company, filled in, set up for a team. It is not a real business.

Put anything private (notes, contracts, credentials you must keep nearby) in `private/`. It is never committed to git and the guard keeps the AI out of it (in Claude Code and OpenCode). Still, do not put passwords there: see "What the guard does not do".

## 3. Pick your path

### Path A: Claude Code

1. `cd ~/aios`
2. `cs` (or `cr`). Claude Code opens and runs `/prime`.
3. Run `/daily-brief`. It writes `outputs/drafts/daily-brief-<date>.md`.
4. Try `/kpi` to see or add a number, and `/create-plan` before a bigger change.

`CLAUDE.md` is one line that points Claude Code to `AGENTS.md`, the main file. The guard and the session-start hook are set up in `.claude/settings.json`. Claude Code asks you to trust the folder the first time.

### Path B: OpenCode (free)

1. Install OpenCode and pick a model. Free models work: this kit's `/prime` and `/daily-brief` were run on one.
2. `cd ~/aios`, then `opencode`.
3. Type `/prime`, then `/daily-brief`.

OpenCode reads `AGENTS.md` itself. The commands come from `.opencode/commands/`. The guard is the plugin `.opencode/plugins/aios-guard.js`, and `opencode.json` adds OpenCode's own deny rules for `private/`. There is no `cs`/`cr` pair: OpenCode's permission rules are in `opencode.json`.

To run one command without opening the screen: `opencode run --command prime ""`.

### Path C: your own AI (Claude Cowork, Codex, ChatGPT or any other)

Use this if you do not want to work in a terminal. Terminal and Claude Code (Path A) stay the recommended way: `cr` is the fastest start. Here you give your AI the kit and let it tailor the workspace to you:

1. Give it the kit: the link `https://github.com/alrayes-5/aios`, or the folder path if it can open a folder on your computer (Cowork and Codex can). If it can do neither, upload the ZIP, or paste `START_HERE.md`, `AGENTS.md` and the five files in `context/`.
2. Send this prompt, with the link or path filled in:

```text
I want you to set up an AIOS workspace for me. AIOS is a folder of plain files that tells an AI agent who I am, what my business is and what matters now, so every session starts informed.

The kit is here: [paste the link https://github.com/alrayes-5/aios, or the folder path on my computer]

1. Read START_HERE.md, AGENTS.md, the files in context/ and the finished example in example/.
2. Ask me questions, a few at a time, about who I am, what my business is and who it serves, my goals right now, and what is going on this month. Wait for my answers. Do not guess.
3. Write my answers into the five files in context/ (personal-info.md, business-info.md, strategy.md, current-data.md, rules.md), in my own words. Show me each file before you save it, and change nothing until I say yes.
4. In rules.md, ask me what you may do alone, what needs my approval, and what must never go into this workspace. Keep the rules strict.
5. Do not put passwords, API keys or my customers' personal data in any file. Do not send or publish anything for me: you write drafts into outputs/drafts/ and I send them.
6. When you finish, run the steps in commands/prime.md and say back what you understood. If there is a step you cannot do in this tool, say so instead of pretending.
```

3. For a daily brief later, ask it to follow `commands/daily-brief.md` with your latest numbers.

Review what the AI wrote before you rely on it, and keep your own copy of the folder. **There is no guard here.** The guard in step 4 works only in Claude Code and OpenCode. In any other tool, `AGENTS.md` and `context/rules.md` are instructions the AI is asked to follow, nothing more.

## 4. The guard: what it blocks, and where it works

One script, `.aios/guard.py`, holds the policy. Both harnesses call it before every tool call.

It blocks:

1. **Reads and writes of `private/`** by the AI's file tools and by the shell commands it can be read from (Bash, and on Windows PowerShell and `cmd`): `cat private/x`, `Get-Content private\x`, a wildcard such as `pri*`, a `cd` into it, a path that reaches it through `..` or a symlink, and a search that walks the whole workspace (`grep -r`, `find`, `ls -R`, `tar`, `cp -r`, `du`, `tree`) from the workspace root unless it names a folder such as `context/` or excludes `private/` (for example `grep -r term . --exclude-dir=private`). Commands hidden in `bash -c '...'`, `eval`, `powershell -Command` or `cmd /c` are read too. The tools' own search (Grep, Glob, `rg`) skips `private/` because of the `.ignore` file.
2. **Writes outside the workspace folder**, including `curl -o`, `wget -O`, `Set-Content`, `Out-File`, `>` and `Invoke-WebRequest -OutFile`. `/dev/null`, `NUL` and `$null` are fine as places to throw output away.
3. **Edits to a core file:** `AGENTS.md`, `CLAUDE.md`, `context/rules.md`, `opencode.json`, `.ignore`, `.aios/`, `.claude/settings.json`, `.opencode/plugins/`. The AI writes the change it wants as a note in `plans/`, and you apply it. For a maintenance session where the AI may edit core files, start the harness with `AIOS_UNLOCK=1` (for example `AIOS_UNLOCK=1 opencode`). `private/` stays closed even then.

Names are compared without regard to case, so `PRIVATE/` is treated as `private/`. Either slash works, and `C:\...` and Git Bash `/c/...` paths are read as the same place.

| Harness | Guard | How |
| ------- | ----- | --- |
| OpenCode | Enforced (tested) | The plugin `.opencode/plugins/aios-guard.js` calls `guard.py`; `opencode.json` also denies read and edit in `private/` on its own |
| Claude Code | Enforced by a hook (see "What was tested" for what was run, and where) | A `PreToolUse` hook in `.claude/settings.json` calls `guard.py` for Bash, PowerShell and the file tools; `permissions.deny` also lists `private/` |
| Any other AI tool (Cowork, Codex, ChatGPT, ...) | None | Rely on your own care |

### What the guard does not do

- It is **not a sandbox.** For shell commands it reads the command text. It catches the usual cases listed above, but anything it cannot read in the text gets through: a script or a program the AI writes and then runs (Python, Node, a shell script), a path built from pieces (`$(echo priv)ate/x`), or an `awk` or `perl` program that writes a file. The same holds in PowerShell: a `.ps1` script the AI writes and runs, or a path built from pieces such as `'pri'+'vate'`, is not read. A path built from a variable is refused when the command writes, and when it names `private`. It can still reach anything your user account can reach. Inline Python, Node, Perl or Ruby code that names `private` is refused, but code that builds the name in pieces is not.
- It does not stop you. Anything you do in your own terminal or editor is outside it.
- It does not protect a secret. Treat `private/` as a drawer, not a vault. Keep passwords and API keys out of this folder altogether.
- It only works in a harness that loads it. If you open the folder in another agent tool, assume there is no guard until you have tested it: run the check below.

### Check the guard yourself

```bash
python3 scripts/test-guard.py
```

It runs 167 checks against `guard.py` (161 on Windows, where the hook-command checks are skipped) and prints PASS or FAIL for each: file tools, Bash, PowerShell, Windows-style paths, and the hook command run with different Pythons on the PATH. To check it inside your harness, open a fresh copy, put a file in `private/`, and ask the AI to read it: it should be refused with a line starting `AIOS guard:`.

## 5. Automation: a morning brief

`automation/morning-brief.sh` runs `/daily-brief` without opening a session, so the brief is waiting in `outputs/drafts/` when you sit down. Run it by hand once:

```bash
sh automation/morning-brief.sh opencode     # or: claude
```

Then schedule it (cron on macOS and Linux, Task Scheduler on Windows): see [automation/README.md](automation/README.md). The session-start hook (`.aios/session-start.py`) prints today's date and which context files are still templates at the start of each Claude Code session.

## 6. What was tested

Everything not on this list was not tested: treat it as untried.

**Claude Code counts as tested on two grounds only:** Ahmed's own tests of the template (next paragraph), and a live run of this kit in Claude Code 2.1.312 on Ahmed's Windows PC (first bullet below). Nothing more is claimed for the guard in Claude Code.

**The template: the five context files, `/prime`, `/daily-brief`, `/kpi`, the commands, the example company.** Ahmed Elrayes tested these himself, on Windows, in Claude Code, OpenCode, AlphaCode and Codex, with models including Kimi and MiniMax.

**What was added when the kit was packaged: the guard, the hooks, the morning brief and `test-guard.py`.** These were not part of Ahmed's tests. They were checked like this:

- **Claude Code 2.1.312, a live run of this kit on a Windows PC.** The template worked there. The guard did not: path rules written with `/` never matched Windows `\` paths, `/dev/null` was read as a path outside the workspace, the PowerShell tool was not covered by the hook, Git Bash paths such as `/c/Users/...` were misread, and with no working `python3` on the PATH every action was refused. Those are fixed in this version. **This version of the guard has not been run live on Windows.** What was done instead: `python3 scripts/test-guard.py` runs Windows-style paths (backslashes, upper-case letters, `C:\...`), PowerShell and `cmd` commands, and the hook command with only `python` on the PATH, with a `python3` that does not run, and with no Python. A `\` path and a Git Bash `/c/...` path were checked as text rules on Linux, not on a real Windows machine. If the guard lets something through on your Windows PC, please open an issue.
- **OpenCode 1.19.3 with a free model, on Linux, a fresh copy each time:** `/prime`, `/daily-brief` (on the example company), `/kpi`, `automation/morning-brief.sh opencode`; the guard blocking each of: a write to `private/`, a read of `private/`, `cat private/...`, a write to `/tmp`, `sed -i` on `AGENTS.md`, an edit to `AGENTS.md`, `ls pri*`, `grep -rn term .`, `find . -type f -exec cat {} +`, `bash -c 'cat private/...'` and `cat PRIVATE/...`; the guard allowing a write to `outputs/drafts/` and `grep -rn term . --exclude-dir=private`; the OpenCode Grep tool over the whole workspace returning nothing from `private/` (because of `.ignore`); the `AIOS_UNLOCK=1` session; `opencode.json` deny rules on their own. After the last change to the plugin (it now finds `python3`, `python` or `py`), `grep -rn CANARY .` and `bash -c 'cat private/secret.txt'` were run again and both were blocked.
- **The guard script on its own, on Linux:** 167 checks pass (`python3 scripts/test-guard.py`).
- **Claude Code on Linux or macOS:** not run live. The hook command in `.claude/settings.json` was run as Claude Code runs it, with its payload, and blocked what it should.
- **Task Scheduler on Windows (section 5 and `automation/README.md`):** the steps are written from how Task Scheduler and Claude Code work and were not run.
- **Your own AI tool (Path C, the ready prompt):** not tried in Cowork, Codex or ChatGPT.
- **macOS:** not tested.

Free models are less careful than paid ones. If a command does something odd, read the file in `commands/` and tell the AI which step it missed.

## 7. Make it yours

- Edit `context/` as your business changes. `/prime` reads it every session.
- Record numbers with `/kpi`. Keep `data/kpi-tracker.md` to aggregate figures: no customer data.
- Add a command: write `commands/<name>.md`, then copy the two small wrappers in `.claude/commands/` and `.opencode/commands/`.
- When you are done with `example/`, delete it.

AIOS is free under the MIT licence. It was written by Ahmed Elrayes. The `skill-creator` skill in `.claude/skills/` was originally Anthropic's, adapted by OpenAI for Codex and taken from OpenClaw's bundled copy, under Apache 2.0; see [README.md](README.md) and the `NOTICE.md` next to it.
