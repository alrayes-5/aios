# What was tested, and what was not

Everything not listed as run is **not run**: treat it as untried. Dates are 2026-10-28.

## The one thing to know first

No real model was available for the tool runs below. Claude Code on the test machine was not logged in, and OpenCode's free models had hit their usage limit. So the permission tests used the real `claude` (2.1.302) and `opencode` (1.19.3) programs against a small scripted stand-in for the model's server (`mock_api.py` and `mock_oai.py`, not part of the kit). The stand-in makes the tool calls it is told to make, and the real program decides whether to allow them. That tests the permission rules, which are what this kit relies on. It does not test how a real model behaves with the commands.

The daily brief at the top of `README.md` and the `/prime` and `/kpi` checks below were done by a model (Claude Sonnet 5.5, in an agent harness) that read `AGENTS.md` and followed `commands/daily-brief.md`, `commands/prime.md` and `commands/kpi.md` literally in fresh copies of the kit with `example/` loaded. The shell commands were really run; the replies were not typed by hand. This was not done through the `/daily-brief` slash command in Claude Code or OpenCode.

## What was run

**The test suite, on Linux (Python 3.13).** `python3 -m unittest discover -s tests`: 29 tests, all pass. They cover `kpi.py` (add a reading, gap, change since the last reading, stale marking after 7 days, a bad value refused, a duplicate day refused, a value ten times off needs `--confirm`, Python 3.8 syntax), the settings (the protected paths denied in `.claude/settings.json` and `opencode.json`, no bypass mode, no broad `Bash` allow, every command has both wrappers) and the docs (the skip-permissions flag only in `docs/advanced.md`, no em or en dashes, removed files gone, the layer table once, a short README that opens with a brief, no company or secret words).

**Claude Code, default mode, real program, scripted model.** In a fresh copy, run with `claude -p`:

| Tool call | Result |
| --- | --- |
| Edit `commands/prime.md` | refused: "File is in a directory that is denied by your permission settings." |
| Write `AGENTS.md` | refused, same message |
| Write `.claude/commands/prime.md` | refused, same message |
| Bash `echo x > commands/prime.md` | not run: "Permission to use Bash ... has been denied" (no one was there to approve it) |
| Bash `echo x > outputs/drafts/ok.md` | not run: "Output redirection ... needs approval" |
| Bash `python3 scripts/kpi.py status` | not run: "This command requires approval" |
| Write `plans/ok.md` (in `acceptEdits` mode) | allowed |

The files were unchanged afterwards (`git status --porcelain` empty). A `/prime` typed in this run expanded to the wrapper text "Read the file `commands/prime.md` ...", so the wrapper loads. With one protected file changed, the `git status --porcelain` line in `/prime` printed ` M commands/prime.md`.

**The morning brief flags (`automation/morning-brief.sh`, Claude Code branch).** With its `--allowedTools` list, `scripts/kpi.py status` ran, a write to `outputs/drafts/` succeeded and a write to `AGENTS.md` was refused. The real `/daily-brief` was not run unattended.

**The skip-permissions flag, as warned in `docs/advanced.md`.** With the flag on, Edit and Write to protected files were still refused, a shell redirect or `sed -i` on a protected file was still refused, but any other shell command ran without asking (`echo x > outputs/drafts/ok.md`), `python3 -c "open('commands/prime.md','w').write('x')"` rewrote a protected file and `echo y > ../outside-test.txt` wrote a file outside the folder. That is why the flag is in an appendix, with the warning first.

**OpenCode, real program, scripted model** (permission rules from `opencode.json`):

| Tool call | Result |
| --- | --- |
| edit `commands/prime.md` | refused by the rule on `commands/*` |
| write `AGENTS.md` | refused by the rule on `AGENTS.md` |
| bash `echo x > commands/prime.md` | asked; with no one to answer, "auto-rejecting", and the file was unchanged |
| write `outputs/drafts/ok.md` (run with auto-approve on) | allowed |
| bash `python3 scripts/kpi.py add "Shop revenue" 9.4 --source "till report"` (auto-approve on) | ran; `data/kpis.csv` got one new line |

With auto-approve on, OpenCode runs shell commands without asking, as `cr` does in Claude Code: do not use it for work you have not read.

**`/kpi add` through the script, on a fresh copy of `example/`.** Added `Shop revenue 9.4` with source `till report`: the script printed the new status table, and `git diff --stat` showed `data/kpis.csv | 1 +`. A second reading on the same day, a non-number and a value ten times off were refused. With "today" moved to 2026-11-10, rows older than 7 days were marked `STALE`.

**`/prime` and `/daily-brief`** on the `example/` copy, by a model following the command files: `/prime` ran the protected-file check (empty), found no template text, ran the KPI script and said back who the user is, the structure, the strategy and three limits from `rules.md`. `/daily-brief` ran the script, listed `plans/` and `outputs/drafts/`, and wrote `outputs/drafts/daily-brief-2026-10-28.md`: the gap and change figures in it are the script's.

**The update steps (`UPDATING.md`, bash).** Run in a scratch copy with local folders in place of the GitHub clone: the copy and delete steps changed only kit files, and `context/`, `data/`, `outputs/` and `plans/` were identical afterwards.

## Not run

- **Claude Code's sandbox.** It is turned on in `.claude/settings.json`. Its documentation says `Edit` deny rules are merged into the sandbox's filesystem rules, which would stop a shell command from writing a protected file on macOS, Linux and WSL2. On the test machine the sandbox could not start (`bubblewrap` and `socat` not installed), so that was not seen working. On native Windows there is no sandbox. Shell commands still ask you either way.
- **A real model through `/prime`, `/daily-brief` and `/kpi` in Claude Code or OpenCode** (see the top of this page).
- **Windows and macOS.** The CI workflow in `.github/workflows/test.yml` runs the suite on ubuntu, macos and windows, and on Python 3.8, but it has not run yet. Task Scheduler (`automation/README.md`) was not run.
- **Cursor, Codex, Claude Cowork, ChatGPT** with the Path C prompt.
- **A real model trying to get round a refusal.**

## Before v1.1

Ahmed Elrayes tested the template (the context files, `/prime`, `/daily-brief`, `/kpi`, the example company) himself, on Windows, in Claude Code, OpenCode, AlphaCode and Codex, with models including Kimi and MiniMax. The v1 shell guard was tested separately and is gone in v1.1, replaced by the tools' own permission rules above.
