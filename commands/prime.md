# Prime

Start of every session. Load the workspace, check that the protected files are untouched, then say back what you understood.

## Steps

1. Run `git status --porcelain -- AGENTS.md CLAUDE.md context/rules.md commands .claude .opencode opencode.json scripts automation .github`. These are the protected files. If it prints anything, a protected file was changed or added since the last commit. If this folder is not a git repository, note that instead (the fix is in `START_HERE.md`, step 2).
2. List the files in the workspace root and in `context/`, `data/` and `commands/`.
3. Read `AGENTS.md` (skip it if your harness already loaded it) and every file in `context/`, including `rules.md`.
4. Check each file in `context/` for template text: a line that starts with `[` and ends with `]`, or an empty bullet. List the files that are still templates.
5. Run `python3 scripts/kpi.py status` (if `python3` is not found, use `python`, then `py`), only to know whether there are numbers yet.

## Report

Reply in this order, briefly:

1. **At the very top, only if step 1 found a change:** "Protected file changed:" and the list, or "This folder is not a git repository". Say that it may be the user's own edit or something that should not be there, and ask them to check with `git diff` before you go on. If there is nothing to report, leave this out.
2. Who I am, what this workspace is for, and what your role is.
3. The workspace structure and what each folder is for.
4. The commands available (`/prime`, `/plan`, `/kpi`, `/daily-brief`).
5. My current strategy and priorities, from `context/strategy.md`. If the file is still a template, say so.
6. Files in `context/` that are still templates. If any, offer to fill them in with me by asking one short question at a time. Write each answer into the file only after I confirm it.
7. Confirm you are ready, and read back the three limits from `context/rules.md` that matter most today.
