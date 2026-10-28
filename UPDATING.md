# Updating

Kit files and your files are kept apart. An update replaces the kit files and **never touches** `context/`, `data/`, `outputs/` or `plans/`.

| Yours (an update never touches them) | The kit's (an update replaces them) |
| --- | --- |
| `context/`, `data/`, `outputs/`, `plans/`, `reference/`, `example/` | `AGENTS.md`, `CLAUDE.md`, `commands/`, `scripts/`, `automation/`, `tests/`, `.claude/`, `.opencode/`, `opencode.json`, `.github/`, `docs/`, the root `.md` files, `LICENSE` |

If you changed a kit file yourself (a command, `opencode.json`, a permission rule), the update overwrites that change: copy it somewhere first. The same goes for `.claude/settings.local.json`, if you have one: the update replaces the whole `.claude/` folder.

## Steps (macOS, Linux, Git Bash)

Run these from inside your AIOS folder, which must be a git repository (see `START_HERE.md`, step 2).

```bash
git add -A && git commit -m "before AIOS update" --allow-empty
git clone --depth 1 --branch v1.1 https://github.com/alrayes-5/aios.git ../aios-new
for p in AGENTS.md CLAUDE.md START_HERE.md UPDATING.md TESTING.md CHANGELOG.md README.md LICENSE opencode.json .gitignore .gitattributes; do cp "../aios-new/$p" "$p"; done
for d in commands scripts automation tests docs .claude .opencode .github; do rm -rf "$d" && cp -R "../aios-new/$d" "$d"; done
rm -rf ../aios-new
git status
git diff --stat
```

Replace `v1.1` with the tag you want (the list is on the repository's Releases and Tags page). `git status` should show changes only in kit files. If it shows a file under `context/`, `data/`, `outputs/` or `plans/`, run `git checkout -- <file>`: nothing in the steps above writes there.

Then read the entry for the new version in [CHANGELOG.md](CHANGELOG.md), delete the files it says were removed, and run `/prime`.

## Steps (Windows PowerShell)

```powershell
git add -A; git commit -m "before AIOS update" --allow-empty
git clone --depth 1 --branch v1.1 https://github.com/alrayes-5/aios.git ..\aios-new
foreach ($p in 'AGENTS.md','CLAUDE.md','START_HERE.md','UPDATING.md','TESTING.md','CHANGELOG.md','README.md','LICENSE','opencode.json','.gitignore','.gitattributes') { Copy-Item "..\aios-new\$p" $p -Force }
foreach ($d in 'commands','scripts','automation','tests','docs','.claude','.opencode','.github') { Remove-Item $d -Recurse -Force -ErrorAction SilentlyContinue; Copy-Item "..\aios-new\$d" $d -Recurse -Force }
Remove-Item ..\aios-new -Recurse -Force
git status
```

## Upgrading from v1 (the first release)

Do the steps above, then also:

1. Delete what v1.1 removed: `.aios/` (the guard), `private/`, `.ignore`, `.claude/skills/`, `.opencode/plugins/`, `scripts/test-guard.py`, `scripts/shell-aliases.md`, `commands/create-plan.md`, `commands/implement.md` and their four wrappers. Before you delete `private/`, move anything you keep there out of this folder.
2. Move your numbers: v1 kept them in `data/kpi-tracker.md`. v1.1 keeps them in `data/kpis.csv` and `data/targets.csv`, written by `scripts/kpi.py`. Re-enter them with `/kpi define` and `/kpi add` (give each a date with `--date` and a source). Then delete `data/kpi-tracker.md`.
3. If your shell has `cr`, remove it or keep it knowing what it does: see [docs/advanced.md](docs/advanced.md).
