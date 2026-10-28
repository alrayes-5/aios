# Prime

Start of every session. Load the workspace, then say back what you understood.

## Steps

1. List the files in the workspace root and in `context/`, `data/` and `commands/`.
2. Read `AGENTS.md` (skip it if your harness already loaded it) and every file in `context/`, including `rules.md`.
3. Read `data/kpi-tracker.md`, only to know whether it has numbers yet.
4. Do not open `private/`. It is the person's own folder, and the guard blocks it.
5. Check each file in `context/` for template text: a line that starts with `[` and ends with `]`, or an empty bullet. List the files that are still templates.

## Report

Reply in this order, briefly:

1. Who I am, what this workspace is for, and what your role is.
2. The workspace structure and what each folder is for.
3. The commands available (`/prime`, `/create-plan`, `/implement`, `/kpi`, `/daily-brief`).
4. My current strategy and priorities, from `context/strategy.md`. If the file is still a template, say so.
5. Files in `context/` that are still templates. If any, offer to fill them in with me by asking one short question at a time. Write each answer into the file only after I confirm it.
6. Confirm you are ready, and read back the three limits from `context/rules.md` that matter most today.
